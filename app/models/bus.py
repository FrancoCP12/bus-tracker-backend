"""Modelo de autobús."""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from app.db.base import Base


class Bus(Base):
    __tablename__ = "bus"

    id_bus: Mapped[int] = mapped_column(primary_key=True)
    id_route: Mapped[int | None] = mapped_column(
        ForeignKey("route.id_route"), nullable=True
    )
    patent: Mapped[str] = mapped_column(String(7), unique=True)
    identifier: Mapped[str] = mapped_column(String(10))
    company: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __str__(self) -> str:
        return f"Bus({self.identifier})"
