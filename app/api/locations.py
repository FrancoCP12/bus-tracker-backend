from fastapi import APIRouter, Depends, Query
from app.repositories.route_repository import search_buses_by_location
from sqlalchemy.orm import Session
from app.db.base import get_db

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/search/")
def search_bus(
    lat_origen: float = Query(..., description="Latitud del punto de origen"),
    lon_origen: float = Query(..., description="Longitud del punto de origen"),
    lat_destiny: float = Query(..., description="Latitud del punto de destino"),
    lon_destiny: float = Query(..., description="Longitud del punto de destino"),
    db: Session = Depends(get_db),
):
    return search_buses_by_location(
        db, lat_origen, lon_origen, lat_destiny, lon_destiny
    )
