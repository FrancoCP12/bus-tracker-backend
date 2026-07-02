from dataclasses import asdict
from sqlalchemy.orm import Session
from app.domain.interfaces.bus_repository import IBusRepository
from app.domain.entities.bus import Bus
from app.domain.value_objects import BusFilter
from app.models.bus import Bus as BusModel


def _to_domain(model: BusModel) -> Bus:
    return Bus(
        id_bus=model.id_bus,
        id_route=model.id_route,
        patent=model.patent,
        identifier=model.identifier,
        company=model.company,
        is_active=model.is_active,
    )


class SQLBusRepository(IBusRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_all(self, filter: BusFilter | None = None) -> list[Bus]:
        query = self._session.query(BusModel)
        if filter:
            if filter.id:
                query = query.filter(BusModel.id_bus == filter.id)
            if filter.patent:
                query = query.filter(BusModel.patent == filter.patent)
            if filter.identifier:
                query = query.filter(BusModel.identifier == filter.identifier)
            if filter.company:
                query = query.filter(BusModel.company == filter.company)
            if filter.is_active is not None:
                query = query.filter(BusModel.is_active == filter.is_active)
        return [_to_domain(b) for b in query.all()]

    def get_by_id(self, bus_id: int) -> Bus | None:
        result = self._session.query(BusModel).filter(BusModel.id_bus == bus_id).first()
        return _to_domain(result) if result else None

    def get_by_patent(self, patent: str) -> Bus | None:
        result = self._session.query(BusModel).filter(BusModel.patent == patent).first()
        return _to_domain(result) if result else None

    def create(self, bus: Bus) -> Bus:
        db_bus = BusModel(**asdict(bus))
        self._session.add(db_bus)
        self._session.commit()
        self._session.refresh(db_bus)
        return _to_domain(db_bus)

    def update(self, bus_id: int, updates: dict) -> Bus:
        db_bus = self._session.query(BusModel).filter(BusModel.id_bus == bus_id).first()
        for key, value in updates.items():
            setattr(db_bus, key, value)
        self._session.commit()
        self._session.refresh(db_bus)
        return _to_domain(db_bus)
