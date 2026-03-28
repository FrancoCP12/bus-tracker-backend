"""
Modelo de parada de autobús.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey
from geoalchemy2 import Geometry
from app.db.base import Base


class BusStop(Base):
    """
    Modelo de parada de autobús.
    
    Attributes:
        id_bus_stop: Identificador único de la parada
        id_route: FK a la ruta asociada
        position: Geometría Point con ubicación (SRID 4326)
    """
    __tablename__ = 'bus_stop'

    id_bus_stop: Mapped[int] = mapped_column(primary_key=True)
    id_route: Mapped[int] = mapped_column(ForeignKey('route.id_route'))
    position: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True)
    )
