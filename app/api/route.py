from fastapi import HTTPException
from app.services.eta_service import get_distance_to_stop
from app.services.eta_service import calculate_speed
from app.services.route_service import next_bus_stop
from starlette.status import HTTP_400_BAD_REQUEST
from app.services.route_service import get_buses_by_busStop
from app.services.location_service import redis
from typing import Any
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.route_service import toGeoJson, get_bus_stops, GeoJson
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post('/geojson/')
def store_route(
    geojson: GeoJson,
    db: Session = Depends(get_db)
):
    """
    Almacena una ruta y sus paradas desde formato GeoJSON.
    
    Espera un GeoJSON con features de tipo 'route' y 'bus_stop'.
    Las paradas existentes se reutilizan si están dentro de 15m.
    
    Args:
        geojson: Objeto con string GeoJSON
        db: Sesión de base de datos
        
    Returns:
        Mensaje de confirmación
    """
    return toGeoJson(geojson, db)


@router.get("/busStop/{user_lat}/{user_lon}")
def get_bus_stop(
    user_lat: float,
    user_lon: float,
    db: Session = Depends(get_db)
):
    """
    Obtiene paradas de autobus cercanas a una ubicación.
    
    Busca paradas dentro de 500 metros del punto dado.
    
    Args:
        user_lat: Latitud del usuario
        user_lon: Longitud del usuario
        db: Sesión de base de datos
        
    Returns:
        Lista de paradas cercanas
    """
    return get_bus_stops(user_lat, user_lon, db)

@router.get('/buses/eta/')
async def get_eta(
    id_bus: int | None,
    company: str | None, 
    stop_id: int | None, 
    session: Session = Depends(get_db)
    )-> dict[str, dict[str, Any]]:

    """
    Obtiene el tiempo estimado de un bus para llegar a una parada especifica o a la mas cercana

    Args:
        id_bus: ID del bus
        company: Compañia de transporte
        stop_id: ID de la parada de bus
        session: Sesion de base de datos
    
    Returns:
        Diccionario como clave el ID del bus y como valor un diccionario con las caracteristicas del bus
        en el momento del llamado
    """

    bus_data: dict[str, list[float]] = {}
    id_stop = stop_id
    if id_bus or company:
        async for data in redis.get_location(company, id_bus):
            if data.get("buses", {}).get(id_bus):
                bus_data[f"{id_bus}"] = data["buses"][id_bus]
                break
    
    elif stop_id:
        for bus in get_buses_by_busStop(stop_id, session):
            async for data in redis.get_location(id_bus=bus):
                if data.get("buses", {}).get(bus):
                    bus_data[f"{bus}"] = data["buses"][bus]
                    break
    else:
       raise HTTPException(status_code=400, detail="Parámetros inválidos")

    if not stop_id:
        bus_lat = bus_data[f"{id_bus}"][0]
        bus_lon = bus_data[f"{id_bus}"][1]
        id_stop = next_bus_stop(id_bus, bus_lat, bus_lon, session)
    
    buses_eta = {}
    for bus_id in list(bus_data.keys()):

        bus_lat = bus_data[f"{id}"][0]
        bus_lon = bus_data[f"{id}"][1]
        timestamp = bus_data[f"{id}"][2]
        velocity = calculate_speed(bus_data[f"{id}"])
        distance = get_distance_to_stop(session, bus_lon, bus_lat, id_stop)
        eta = distance/velocity if velocity > 0 else "waiting"

        buses_eta[f"{id}"] = {
            "coord" : [bus_lon, bus_lat],
            "timestamp": timestamp,
            "velocity" : velocity,
            "distance": distance,
            "ETA": eta
            }

    return buses_eta