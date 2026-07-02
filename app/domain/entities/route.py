from dataclasses import dataclass


@dataclass
class BusStop:
    id_bus_stop: int | None = None
    id_route: int | None = None
    position: str | None = None


@dataclass
class Route:
    id_route: int | None = None
    position: str | None = None
