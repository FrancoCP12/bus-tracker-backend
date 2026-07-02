from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class ILocationService(ABC):
    @abstractmethod
    async def get_location(
        self, id_bus: str | None = None, company: str | None = None
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def set_location(self, bus: dict[str, Any]) -> bool: ...

    @abstractmethod
    async def subscribe(
        self, company: str | None = None, id_bus: str | None = None
    ) -> AsyncGenerator[dict[str, Any], None]: ...
