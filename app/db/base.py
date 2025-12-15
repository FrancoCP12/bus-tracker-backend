from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from typing import Any
import os

load_dotenv()

postgress_url: str | Any = os.getenv("DATABASE_URL")
print(postgress_url)
engine = create_engine(postgress_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass