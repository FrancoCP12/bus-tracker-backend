from fastapi import Depends, APIRouter, HTTPException
from app.db.base import get_db
from app.schemas.bus import BusCreate, BusResponse, BusUpdate
from app.repositories.bus_repository import (
    get_all,
    get_by_patent,
    create as create_bus_repo,
    update as update_bus_repo,
)
from app.models.bus import Bus
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/buses", tags=["buses"])


@router.get("/", response_model=list[BusResponse])
def list_buses(
    id: Optional[int] = None,
    patent: Optional[str] = None,
    identifier: Optional[str] = None,
    company: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return get_all(db, id, patent, identifier, company, is_active)


@router.post("/", response_model=BusResponse)
def create_bus(bus: BusCreate, db: Session = Depends(get_db)):
    if get_by_patent(db, bus.patent):
        raise HTTPException(status_code=400, detail="Bus already exists")

    new_bus = Bus(**bus.model_dump())
    return create_bus_repo(db, new_bus)


@router.patch("/{bus_id}", response_model=BusResponse)
def update_bus(bus_id: int, bus: BusUpdate, db: Session = Depends(get_db)):
    db_bus = get_all(db, id=bus_id)[0] if get_all(db, id=bus_id) else None
    if not db_bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    updates = bus.model_dump(exclude_unset=True)
    return update_bus_repo(db, db_bus, updates)
