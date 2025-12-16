from pydantic import BaseModel

class BusCreate(BaseModel):
    patent: str
    identifier : str
    company: str
    is_active: bool

class BusResponse(BaseModel):
    id: int
    patent: str
    identifier: str
    company: str
    is_active: bool

    class Config:
        from_attributes = True