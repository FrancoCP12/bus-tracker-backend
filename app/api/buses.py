from fastapi import Depends, FastAPI
from app.db.base import SessionLocal
from app.schemas.bus import BusCreate, BusResponse
from app.models.bus import Bus
from pydantic import BaseModel

app = FastAPI()
session = SessionLocal()

class SearchBy(BaseModel):

    def __init__(self, id: int | None = None, patent: str | None = None, identifier: str | None = None, is_active: bool | None = None):
        self.id = id
        self.patent = patent
        self.identifier = identifier
        self.is_active = is_active

    def apply_query(self, db_buses): 
        if self.id:
            db_buses = db_buses.filter(Bus.id == self.id)
        if self.patent:
            db_buses = db_buses.filter(Bus.patent == self.patent)
        if self.identifier:
            db_buses = db_buses.filter(Bus.identifier == self.identifier)
        if self.is_active is not None:
            db_buses = db_buses.filter(Bus.is_active == self.is_active)
        return db_buses 
    
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/buses/', response_model=BusResponse)
def return_bus(filters: SearchBy = Depends(SearchBy), db: SessionLocal = Depends(get_db)): # type: ignore
    query = db.query(Bus)
    query = filters.apply_query(query)
    return query

@app.post('/buses/', response_model= BusResponse)
def create_bus(bus: BusCreate, db: SessionLocal = Depends(get_db)): # type: ignore
    db_bus = db.query(Bus).filter(Bus.patent == bus.patent).first()
    if db_bus:
        raise HTTPException(status_code = 400, detail= 'Bus already created') #type: ignore
    
    new_bus = Bus(patent = bus.patent, identifier = bus.identifier, company = bus.company, is_active = bus.is_active)
    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)
    return new_bus
