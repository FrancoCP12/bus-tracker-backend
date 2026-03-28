from fastapi import Depends, APIRouter, HTTPException
from app.db.base import SessionLocal
from app.schemas.bus import BusCreate, BusResponse, BusUpdate
from app.models.bus import Bus
from typing import Annotated, Optional, List
from sqlalchemy.orm import Query

router = APIRouter()


class SearchBy:
    """
    Filtros de búsqueda para listado de autobuses.
    
    Todos los campos son opcionales. Se aplican como AND.
    """
    
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

    def apply_query(self, db_buses: Query) -> Query:
        """Aplica los filtros activos a la query."""
        if self.id:
            db_buses = db_buses.filter(Bus.id_bus == self.id)
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
    """
    Generador de sesión de base de datos.
    
    Crea una sesión, la cede al endpoint y la cierra al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/buses/', response_model=List[BusResponse])
def return_bus(
    filters: Annotated[SearchBy, Depends(SearchBy)], 
    db: Annotated[SessionLocal, Depends(get_db)]
):
    """
    Lista autobuses con filtros opcionales.
    
    Args:
        filters: Filtros de búsqueda (query params)
        db: Sesión de base de datos
        
    Returns:
        Lista de autobuses que coinciden
    """
    query = db.query(Bus)
    query = filters.apply_query(query)
    return query.all()


@router.post('/buses/', response_model=BusResponse)
def create_bus(
    bus: BusCreate,
    db: Annotated[SessionLocal, Depends(get_db)]
):
    """
    Crea un nuevo autobús.
    
    Args:
        bus: Datos del autobús a crear
        db: Sesión de base de datos
        
    Returns:
        El autobús creado
        
    Raises:
        HTTPException: Si la patente ya existe
    """
    db_bus = db.query(Bus).filter(Bus.patent == bus.patent).first()
    if db_bus:
        raise HTTPException(status_code=400, detail='Bus already created')
    
    new_bus = Bus(
        patent=bus.patent,
        identifier=bus.identifier,
        company=bus.company,
        is_active=bus.is_active
    )
    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)
    return new_bus


@router.patch('/buses/{id}', response_model=BusResponse)
def update_by_id(
    id: int,
    bus: BusUpdate,
    db: Annotated[SessionLocal, Depends(get_db)]
):
    """
    Actualiza parcialmente un autobús por ID.
    
    Solo actualiza los campos proporcionados (no nulos).
    
    Args:
        id: ID del autobús a actualizar
        bus: Campos a modificar
        db: Sesión de base de datos
        
    Returns:
        El autobús actualizado
        
    Raises:
        HTTPException: Si el autobús no existe
    """
    db_bus = db.query(Bus).filter(Bus.id_bus == id).first()
    if not db_bus:
        raise HTTPException(status_code=404, detail='Bus not found')

    if bus.company is not None:
        db_bus.company = bus.company
    if bus.identifier is not None:
        db_bus.identifier = bus.identifier
    if bus.patent is not None:
        db_bus.patent = bus.patent
    if bus.is_active is not None:
        db_bus.is_active = bus.is_active

    db.commit()
    db.refresh(db_bus)
    return db_bus
