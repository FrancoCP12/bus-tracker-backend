"""
Modelos de base de datos para el sistema de tracking de autobuses.
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Table, Column
from geoalchemy2 import Geometry
from app.db.base import Base


route_stop_association = Table(
    'route_stops',
    Base.metadata,
    Column('id_route', Integer, ForeignKey('route.id_route'), primary_key=True),
    Column('id_stop', Integer, ForeignKey('bus_stop.id_bus_stop'), primary_key=True)
)


class Route(Base):
    """
    Modelo de ruta de autobús.
    
    Attributes:
        id_route: Identificador único de la ruta
        position: Geometría Linestring con el recorrido (SRID 4326)
        stops: Lista de paradas asociadas a esta ruta
    """
    __tablename__ = 'route'

    id_route: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=True)
    )
    stops = relationship(
        "BusStop",
        secondary=route_stop_association,
        backref="routes"
    )
