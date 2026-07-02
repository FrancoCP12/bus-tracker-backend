from app.domain.interfaces.bus_repository import IBusRepository
from app.domain.entities.bus import Bus
from app.domain.exceptions import BusAlreadyExists, BusNotFound
from app.domain.value_objects import BusFilter
from app.schemas.bus import BusCreate, BusUpdate


class BusUseCase:
    def __init__(self, repo: IBusRepository):
        self._repo = repo

    def list_buses(
        self,
        id: int | None = None,
        patent: str | None = None,
        identifier: str | None = None,
        company: str | None = None,
        is_active: bool | None = None,
    ) -> list[Bus]:
        filter = BusFilter(id=id, patent=patent, identifier=identifier, company=company, is_active=is_active)
        return self._repo.get_all(filter)

    def create(self, data: BusCreate) -> Bus:
        if self._repo.get_by_patent(data.patent):
            raise BusAlreadyExists()

        bus = Bus(**data.model_dump())
        return self._repo.create(bus)

    def update(self, bus_id: int, data: BusUpdate) -> Bus:
        db_bus = self._repo.get_by_id(bus_id)
        if not db_bus:
            raise BusNotFound()

        updates = data.model_dump(exclude_unset=True)
        return self._repo.update(bus_id, updates)
