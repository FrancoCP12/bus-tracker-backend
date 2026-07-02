from abc import ABC, abstractmethod
from app.domain.entities.bus import Bus
from app.domain.value_objects import BusFilter


class IBusRepository(ABC):
    @abstractmethod
    def get_all(self, filter: BusFilter | None = None) -> list[Bus]: ...

    @abstractmethod
    def get_by_id(self, bus_id: int) -> Bus | None: ...

    @abstractmethod
    def get_by_patent(self, patent: str) -> Bus | None: ...

    @abstractmethod
    def create(self, bus: Bus) -> Bus: ...

    @abstractmethod
    def update(self, bus_id: int, updates: dict) -> Bus: ...
