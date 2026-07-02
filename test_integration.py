"""
Script de integración para probar el flujo completo:
1. Crea ruta con paradas vía GeoJSON
2. Crea un bus asociado a la ruta
3. Envía posición GPS ficticia vía WebSocket a Redis
4. Consulta paradas cercanas, ETA y búsqueda geográfica
"""
import requests
import json
import asyncio
import websockets
import time

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# GeoJSON con una ruta sobre Av. de Mayo (Buenos Aires)
# y 4 paradas a lo largo del recorrido
GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"type": "route"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [-58.383, -34.608],
                    [-58.381, -34.607],
                    [-58.379, -34.606],
                    [-58.377, -34.605],
                    [-58.375, -34.604],
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"type": "bus_stop"},
            "geometry": {"type": "Point", "coordinates": [-58.382, -34.6075]},
        },
        {
            "type": "Feature",
            "properties": {"type": "bus_stop"},
            "geometry": {"type": "Point", "coordinates": [-58.379, -34.606]},
        },
        {
            "type": "Feature",
            "properties": {"type": "bus_stop"},
            "geometry": {"type": "Point", "coordinates": [-58.376, -34.6045]},
        },
        {
            "type": "Feature",
            "properties": {"type": "bus_stop"},
            "geometry": {"type": "Point", "coordinates": [-58.374, -34.6035]},
        },
    ],
}


def test_step(step_num, description, response):
    status = response.status_code if hasattr(response, 'status_code') else 'N/A'
    ok = response.ok if hasattr(response, 'ok') else True
    mark = "✅" if (ok if hasattr(response, 'ok') else status < 500) else "❌"
    print(f"  {mark} Step {step_num}: {description}")
    print(f"     Status: {status}")
    try:
        print(f"     Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"     Response: {response.text[:200] if hasattr(response, 'text') else response}")
    return response.ok if hasattr(response, 'ok') else (status < 500)


def main():
    print("\n" + "=" * 60)
    print("TEST DE INTEGRACIÓN - Bus Tracker API")
    print("=" * 60)

    # Step 1: Crear un bus
    bus_id = None
    print("\n📦 Step 1: Crear bus")
    for patent in ["INTEG01", "INTEG02", "INTEG03", "INTEG04"]:
        bus_data = {"patent": patent, "identifier": "BUS-INT", "company": "TestCo", "is_active": True}
        r = requests.post(f"{BASE_URL}/buses/", json=bus_data)
        if test_step(1, f"POST /buses/ ({patent})", r):
            bus_id = r.json()["id_bus"]
            print(f"   Bus creado: id_bus={bus_id}")
            break
        if r.status_code == 400 and "already exists" in r.text.lower():
            continue
    if bus_id is None:
        r = requests.get(f"{BASE_URL}/buses/")
        if r.ok and r.json():
            bus_id = r.json()[0]["id_bus"]
            print(f"   Usando bus existente: id_bus={bus_id}")
        else:
            print("   ❌ No se pudo crear/encontrar un bus. Abortando.")
            return

    # Step 2: Crear ruta con paradas desde GeoJSON
    print(f"\n🗺️  Step 2: Crear ruta desde GeoJSON (bus_id={bus_id})")
    r = requests.post(f"{BASE_URL}/routes/geojson/", params={"geojson": json.dumps(GEOJSON), "bus_id": bus_id})
    test_step(2, "POST /routes/geojson/", r)

    # Step 3: Ver paradas cercanas a un punto
    stop_id = None
    stops = []
    print("\n📍 Step 3: Buscar paradas cercanas")
    r = requests.get(f"{BASE_URL}/routes/bus-stop/-34.606/-58.379")
    test_step(3, "GET /routes/bus-stop/-34.606/-58.379", r)
    if r.ok:
        stops = r.json()
        print(f"     Paradas encontradas: {len(stops)}")
        if stops:
            stop_id = stops[0].get("id_bus_stop")
            print(f"     stop_id de referencia: {stop_id}")

    # Step 4: Enviar posición GPS del bus vía WebSocket
    print("\n🚌 Step 4: Enviar posición GPS del bus vía WebSocket")
    bus_coords = [
        [-58.383, -34.608, time.time()],
        [-58.381, -34.607, time.time() + 5],
        [-58.379, -34.606, time.time() + 10],
        [-58.377, -34.605, time.time() + 15],
    ]
    sent = asyncio.run(send_websocket_positions(bus_id, "TestCo", bus_coords))
    if sent:
        print(f"  ✅ Step 4: {sent} posiciones enviadas vía WebSocket")
    else:
        print(f"  ❌ Step 4: Error enviando posiciones WebSocket")

    # Step 5: Leer ubicación desde Redis vía API
    print("\n🔄 Step 5: Consultar ubicación del bus")
    # No hay endpoint REST para esto directamente, pero podemos ver ETA

    # Step 6: Calcular ETA
    print("\n⏱️  Step 6: Calcular ETA")
    r = requests.get(f"{BASE_URL}/routes/buses/eta/", params={"id_bus": bus_id})
    test_step(6, f"GET /routes/buses/eta/?id_bus={bus_id}", r)

    # Step 7: ETA con stop_id
    print("\n⏱️  Step 7: Calcular ETA con stop_id")
    if stops:
        r = requests.get(f"{BASE_URL}/routes/buses/eta/", params={"stop_id": stop_id})
        test_step(7, f"GET /routes/buses/eta/?stop_id={stop_id}", r)
    else:
        r = requests.get(f"{BASE_URL}/routes/buses/eta/", params={"stop_id": 1})
        test_step(7, f"GET /routes/buses/eta/?stop_id=1", r)

    # Step 8: ETA sin parámetros (debe dar 400)
    print("\n⚠️  Step 8: ETA sin parámetros (debe fallar)")
    r = requests.get(f"{BASE_URL}/routes/buses/eta/")
    test_step(8, "GET /routes/buses/eta/ (sin params)", r)

    # Step 9: Búsqueda por ubicación (origen y destino)
    print("\n🔍 Step 9: Búsqueda de buses entre dos puntos")
    r = requests.post(
        f"{BASE_URL}/locations/search/",
        params={
            "lat_origin": -34.608,
            "lon_origin": -58.383,
            "lat_dest": -34.604,
            "lon_dest": -58.375,
        },
    )
    test_step(9, "POST /locations/search/", r)

    print("\n" + "=" * 60)
    print("FIN DEL TEST DE INTEGRACIÓN")
    print("=" * 60)


async def send_websocket_positions(bus_id, company, coords):
    """Envía posiciones GPS vía WebSocket al endpoint de recepción."""
    try:
        uri = f"{WS_URL}/realtime/buses/{bus_id}/location/"
        async with websockets.connect(uri) as websocket:
            print(f"     WebSocket conectado a {uri}")
            for coord in coords:
                msg = {
                    "id": str(bus_id),
                    "company": company,
                    "coord": coord,
                }
                await websocket.send(json.dumps(msg))
                print(f"     Enviado: {msg}")
                await asyncio.sleep(1)
            # Esperar un poco para que se procese
            await asyncio.sleep(2)
        return len(coords)
    except Exception as e:
        print(f"     Error WebSocket: {e}")
        return 0


if __name__ == "__main__":
    main()
