from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import  ForeignKey
from app.db.base import Base

class Location(Base):
    __tablename__ = 'location'

    id: Mapped[int]= mapped_column(primary_key=True)
    bus_id: Mapped[int]= mapped_column(ForeignKey('bus.id'))
    latitude: Mapped[float] = mapped_column()
    longitud: Mapped[float] = mapped_column()
    timestamp: Mapped[int] = mapped_column()
    
    def __str__(self) -> str:
        position: str = f"{self.latitude}, {self.longitud}\n"
        return position
    
