from fastapi import APIRouter, Depends
from app.schemas.bus import BusCreate, BusResponse, BusUpdate
from app.use_cases.bus import BusUseCase
from app.domain.exceptions import BusAlreadyExists, BusNotFound
from app.api.dependencies import get_bus_use_case
from fastapi import HTTPException

router = APIRouter(prefix="/buses", tags=["buses"])


@router.get("/", response_model=list[BusResponse])
def list_buses(
    id: int | None = None,
    patent: str | None = None,
    identifier: str | None = None,
    company: str | None = None,
    is_active: bool | None = None,
    uc: BusUseCase = Depends(get_bus_use_case),
):
    return uc.list_buses(id, patent, identifier, company, is_active)


@router.post("/", response_model=BusResponse)
def create_bus(bus: BusCreate, uc: BusUseCase = Depends(get_bus_use_case)):
    try:
        return uc.create(bus)
    except BusAlreadyExists:
        raise HTTPException(status_code=400, detail="Bus already exists")


@router.patch("/{bus_id}", response_model=BusResponse)
def update_bus(bus_id: int, bus: BusUpdate, uc: BusUseCase = Depends(get_bus_use_case)):
    try:
        return uc.update(bus_id, bus)
    except BusNotFound:
        raise HTTPException(status_code=404, detail="Bus not found")
