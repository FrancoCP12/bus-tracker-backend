"""
Modelo de autobús.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from app.db.base import Base


class Bus(Base):
    """
    Modelo de autobús.
    
    Representa un vehículo de transporte público en el sistema.
    
    Attributes:
        id_bus: Identificador único del autobús
        id_route: FK a la ruta asignada actualmente
        patent: Patente del vehículo (única)
        identifier: Identificador público visible para usuarios
        company: Empresa propietaria del vehículo
        is_active: Estado activo/inactivo
    """
    __tablename__ = 'bus'

    id_bus: Mapped[int] = mapped_column(primary_key=True)
    id_route: Mapped[int] = mapped_column(ForeignKey("route.id_route"))
    patent: Mapped[str] = mapped_column(String(7), unique=True)
    identifier: Mapped[str] = mapped_column(String(10))
    company: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __str__(self) -> str:
        return f"Bus({self.identifier})"
