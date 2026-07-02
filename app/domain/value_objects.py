from dataclasses import dataclass


@dataclass
class BusFilter:
    id: int | None = None
    patent: str | None = None
    identifier: str | None = None
    company: str | None = None
    is_active: bool | None = None
