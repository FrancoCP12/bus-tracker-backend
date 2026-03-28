from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from app.models.bus_stop import BusStop
from app.models.route import Route
from geoalchemy2.functions import ST_DWithin, ST_LineLocatePoint
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased
from app.db.base import get_db

router = APIRouter()


@router.post("/loadBus/")
def search_bus(
    lat_origen: float = Query(..., description="Latitud del punto de origen"),
    lon_origen: float = Query(..., description="Longitud del punto de origen"),
    lat_destiny: float = Query(..., description="Latitud del punto de destino"),
    lon_destiny: float = Query(..., description="Longitud del punto de destino"),
    session: Session = Depends(get_db),
):
    """
    Busca rutas de autobus que pasen cerca del origen y destino dados.
    
    Busca paradas dentro de un radio de ~500m de cada punto
    y filtra rutas donde el origen aparece antes que el destino en la ruta.
    
    Args:
        lat_origen: Latitud del punto de origen
        lon_origen: Longitud del punto de origen
        lat_destiny: Latitud del punto de destino
        lon_destiny: Longitud del punto de destino
        session: Sesión de base de datos
        
    Returns:
        Lista de ids de rutas que coinciden con los criterios
    """
    user_point = f'SRID=4326;POINT({lon_origen} {lat_origen})'
    final_point = f'SRID=4326;POINT({lon_destiny} {lat_destiny})'

    P_Origen = aliased(BusStop)
    P_Destiny = aliased(BusStop)
    
    stmt = (
        select(Route.id_route)
        .join(P_Origen, Route.id_route == P_Origen.id_route)
        .join(P_Destiny, Route.id_route == P_Destiny.id_route)
        .where(
            and_(
                ST_DWithin(P_Origen.position, user_point, 0.0045),
                ST_DWithin(P_Destiny.position, final_point, 0.0045),
                ST_LineLocatePoint(Route.position, P_Origen.position) < 
                ST_LineLocatePoint(Route.position, P_Destiny.position)
            )
        )
        .distinct()
    )
    
    result = session.execute(stmt).scalars().all()
    return result
