from fastapi import Depends, APIRouter, HTTPException
from app.db.base import SessionLocal
from app.schemas.bus import BusCreate, BusResponse, BusUpdate
from app.models.bus import Bus
from typing import Optional, List

router =  APIRouter()

class SearchBy():

    def __init__(
            self, 
            id: Optional[int] = None, 
            patent: Optional[str] = None, 
            identifier: Optional[str] = None, 
            is_active: Optional[bool] = None,
            company: Optional[str] = None
        ):
        self.id = id
        self.patent = patent
        self.identifier = identifier
        self.is_active = is_active
        self.company = company

    def apply_query(self, db_buses): 
        if self.id:
            db_buses = db_buses.filter(Bus.id == self.id)
        if self.patent:
            db_buses = db_buses.filter(Bus.patent == self.patent)
        if self.identifier:
            db_buses = db_buses.filter(Bus.identifier == self.identifier)
        if self.company:
            db_buses = db_buses.filter(Bus.company == self.company)
        if self.is_active is not None:
            db_buses = db_buses.filter(Bus.is_active == self.is_active)
        return db_buses 
    

    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/buses/', response_model=List[BusResponse])
def return_bus(filters: SearchBy = Depends(SearchBy), db: SessionLocal = Depends(get_db)): # type: ignore
    query = db.query(Bus)
    query = filters.apply_query(query)
    return query.all()

@router.post('/buses/', response_model= BusResponse)
def create_bus(bus: BusCreate, db: SessionLocal = Depends(get_db)): # type: ignore
    db_bus = db.query(Bus).filter(Bus.patent == bus.patent).first()
    if db_bus:
        raise HTTPException(status_code = 400, detail= 'Bus already created') #type: ignore
    
    new_bus = Bus(patent = bus.patent, identifier = bus.identifier, company = bus.company, is_active = bus.is_active)
    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)
    return new_bus

@router.patch('/buses/{id}', response_model= BusResponse)
def update_by_id(id: int, bus: BusUpdate, db: SessionLocal = Depends(get_db)): #type: ignore
    db_bus = db.query(Bus).filter(Bus.id == id).first()
    if not db_bus:
        raise HTTPException(status_code=404, detail= 'Bus not found') #type: ignore

    if bus.company is not None:
        db_bus.company = bus.company
    if bus.identifier is not None:
        db_bus.identifier = bus.identifier
    if bus.patent is not None:
        db_bus.patent = bus.is_active
    if bus.is_active is not None:
        db_bus.is_active = bus.is_active


    db.commit()
    db.refresh(db_bus)
    return db_bus
