from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import String
from app.db.base import Base

class Bus(Base):
    __tablename__ = 'bus'

    id: Mapped[int] = mapped_column( primary_key=True)
    patent: Mapped[str]  = mapped_column(String(7), unique=True)
    identifier: Mapped[str]  = mapped_column(String(10))
    company: Mapped[str]  = mapped_column(String(10))
    is_active : Mapped[bool] = mapped_column()
    
    def __str__(self) -> str:
        return self.identifier


