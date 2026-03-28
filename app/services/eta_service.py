from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_LineLocatePoint
from app.models.bus_stop import BusStop
from app.models.route import Route
from geopy.distance import geodesic
from typing import Any


async def calculate_speed(redis: Any, company: str, id_bus: str) -> float:
    """
    Calcula la velocidad promedio de un autobús basada en su historial.
    
    Args:
        redis: Instancia de ConnectionRedis
        company: Nombre de la empresa
        id_bus: ID del autobús
        
    Returns:
        Velocidad en metros por segundo
    """
    bus_data: dict[str, Any] = {"coords": []}
    
    async for data in redis.get_location(company, id_bus):
        if data.get("buses", {}).get(id_bus):
            bus_data = data["buses"][id_bus]
            break
    
    coords = bus_data.get("coords", [])
    
    if len(coords) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(coords) - 1):
        coord_A = (coords[i][0], coords[i][1])
        coord_B = (coords[i+1][0], coords[i+1][1])
        total_distance += geodesic(coord_A, coord_B).meters

    time_0 = coords[0][2]
    time_1 = coords[-1][2]
    total_time = time_1 - time_0

    if total_time == 0:
        return 0.0

    velocity = total_distance / total_time
    return velocity


def get_distance_to_stop(
    db: Session,
    route_id: int,
    bus_lon: float,
    bus_lat: float,
    stop_id: int
) -> dict[str, float]:
    """
    Calcula distancia y progreso de un autobús respecto a una parada.
    
    Args:
        db: Sesión de base de datos
        route_id: ID de la ruta
        bus_lon: Longitud actual del autobús
        bus_lat: Latitud actual del autobús
        stop_id: ID de la parada destino
        
    Returns:
        Dict con progreso del bus, progreso de parada y distancia en metros
    """
    bus_point = func.ST_SetSRID(func.ST_MakePoint(bus_lon, bus_lat), 4326)
    
    query = db.query(
        ST_LineLocatePoint(Route.position, bus_point).label("bus_progress"),
        ST_LineLocatePoint(Route.position, BusStop.position).label("stop_progress"),
        func.ST_Distance(
            func.ST_LineInterpolatePoint(Route.position, ST_LineLocatePoint(Route.position, bus_point)),
            func.ST_LineInterpolatePoint(Route.position, ST_LineLocatePoint(Route.position, BusStop.position)),
            True 
        ).label("distance_meters")
    ).join(BusStop, BusStop.id_bus_stop == stop_id)\
     .filter(Route.id_route == route_id)\
     .first()

    if query is None:
        return {
            "bus_progress": 0.0,
            "stop_progress": 0.0,
            "distance_meters": 0.0
        }

    return {
        "bus_progress": float(query.bus_progress),
        "stop_progress": float(query.stop_progress),
        "distance_meters": float(query.distance_meters)
    }
