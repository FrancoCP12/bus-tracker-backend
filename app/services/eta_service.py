from app.models.bus import Bus
from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_LineLocatePoint
from app.models.bus_stop import BusStop
from app.models.route import Route
from geopy.distance import geodesic
from typing import Any


async def calculate_speed(coords: list[float]) -> float:
    """
    Calcula la velocidad promedio de un autobús basada en su historial.
    
    Args:
        bus_data: diccionario con los datos de el/los buses  a calcular la velocidad
        
    Returns:
        Velocidad en metros por segundo
    """
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
    bus_lon: float,
    bus_lat: float,
    stop_id: int
) -> float:
    """
    Calcula distancia y progreso de un autobús respecto a una parada.
    
    Args:
        db: Sesión de base de datos
        bus_lon: Longitud actual del autobús
        bus_lat: Latitud actual del autobús
        bus_id: ID del bus
        stop_id: ID de la parada destino
        
    Returns:
        Distancia en metros
    """
    bus_point = func.ST_SetSRID(func.ST_MakePoint(bus_lon, bus_lat), 4326)
    
    query = db.query(
        func.ST_Distance(
            func.ST_LineInterpolatePoint(Route.position, ST_LineLocatePoint(Route.position, bus_point)),
            func.ST_LineInterpolatePoint(Route.position, ST_LineLocatePoint(Route.position, BusStop.position)),
            True 
        )).filter(and_(Bus.id_route == Route.id_route, Bus.id_route == BusStop.id_route, BusStop.id_bus_stop == stop_id))\
        .first()

    if query is None:
        return 0.0
        
    return float(query.distance_meters)
    
