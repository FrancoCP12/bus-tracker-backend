from fastapi import APIRouter, Depends, Query, HTTPException
from app.use_cases.route import RouteUseCase
from app.domain.exceptions import InvalidParameters
from app.api.dependencies import get_route_use_case

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/search/")
def search_bus(
    lat_origin: float = Query(..., description="Latitud del punto de origen"),
    lon_origin: float = Query(..., description="Longitud del punto de origen"),
    lat_dest: float = Query(..., description="Latitud del punto de destino"),
    lon_dest: float = Query(..., description="Longitud del punto de destino"),
    uc: RouteUseCase = Depends(get_route_use_case),
):
    try:
        return uc.search_buses(lat_origin, lon_origin, lat_dest, lon_dest)
    except InvalidParameters:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
