from sqlalchemy.orm import Session
from app.models.bus import Bus
from typing import Optional


def get_by_id(db: Session, bus_id: int) -> Optional[Bus]:
    return db.query(Bus).filter(Bus.id_bus == bus_id).first()


def get_all(
    db: Session,
    id: Optional[int] = None,
    patent: Optional[str] = None,
    identifier: Optional[str] = None,
    company: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    query = db.query(Bus)

    if id:
        query = query.filter(Bus.id_bus == id)
    if patent:
        query = query.filter(Bus.patent == patent)
    if identifier:
        query = query.filter(Bus.identifier == identifier)
    if company:
        query = query.filter(Bus.company == company)
    if is_active is not None:
        query = query.filter(Bus.is_active == is_active)

    return query.all()


def get_by_patent(db: Session, patent: str) -> Optional[Bus]:
    return db.query(Bus).filter(Bus.patent == patent).first()


def create(db: Session, bus: Bus) -> Bus:
    db.add(bus)
    db.commit()
    db.refresh(bus)
    return bus


def update(db: Session, bus: Bus, updates: dict) -> Bus:
    for key, value in updates.items():
        setattr(bus, key, value)
    db.commit()
    db.refresh(bus)
    return bus
