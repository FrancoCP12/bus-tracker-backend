from fastapi import HTTPException, APIRouter, Depends
from app.use_cases.route import RouteUseCase
from app.use_cases.eta import EtaUseCase
from app.domain.exceptions import InvalidParameters, InvalidGeoJson
from app.api.dependencies import get_route_use_case, get_eta_use_case
from typing import Any

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/geojson/")
def store_route(geojson: str, bus_id: int, uc: RouteUseCase = Depends(get_route_use_case)):
    try:
        return uc.create_from_geojson(geojson, bus_id)
    except InvalidGeoJson:
        raise HTTPException(status_code=400, detail="GeoJSON inválido")


@router.get("/bus-stop/{user_lat}/{user_lon}")
def get_bus_stops(user_lat: float, user_lon: float, uc: RouteUseCase = Depends(get_route_use_case)):
    return uc.get_stops_near(user_lat, user_lon)


@router.get("/buses/eta/")
async def get_eta(
    id_bus: int | None = None,
    company: str | None = None,
    stop_id: int | None = None,
    uc: EtaUseCase = Depends(get_eta_use_case),
) -> dict[str, dict[str, Any]]:
    try:
        return await uc.calculate(id_bus, company, stop_id)
    except InvalidParameters:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
