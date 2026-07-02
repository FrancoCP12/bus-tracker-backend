from dataclasses import dataclass


@dataclass
class Bus:
    id_bus: int | None = None
    id_route: int | None = None
    patent: str = ""
    identifier: str = ""
    company: str = ""
    is_active: bool = True
