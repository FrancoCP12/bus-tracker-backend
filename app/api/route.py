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
