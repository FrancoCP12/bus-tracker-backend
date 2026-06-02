from pydantic import BaseModel


class BusCreate(BaseModel):
    patent: str
    identifier: str
    company: str
    is_active: bool = True


class BusUpdate(BaseModel):
    patent: str | None = None
    identifier: str | None = None
    company: str | None = None
    is_active: bool | None = None


class BusResponse(BaseModel):
    id_bus: int
    patent: str
    identifier: str
    company: str
    is_active: bool

    class Config:
        from_attributes = True
