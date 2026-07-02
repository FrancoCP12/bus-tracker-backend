from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.infrastructure.repositories.sqlalchemy.bus_repository import SQLBusRepository
from app.infrastructure.repositories.sqlalchemy.route_repository import SQLRouteRepository
from app.infrastructure.redis.location_service import RedisLocationService, get_location_service
from app.use_cases.bus import BusUseCase
from app.use_cases.eta import EtaUseCase
from app.use_cases.route import RouteUseCase


def get_bus_use_case(db: Session = Depends(get_db)) -> BusUseCase:
    repo = SQLBusRepository(db)
    return BusUseCase(repo)


def get_route_use_case(
    db: Session = Depends(get_db),
    location_svc: RedisLocationService = Depends(get_location_service),
) -> RouteUseCase:
    repo = SQLRouteRepository(db)
    return RouteUseCase(repo, location_svc)


def get_eta_use_case(
    db: Session = Depends(get_db),
    location_service: RedisLocationService = Depends(get_location_service),
) -> EtaUseCase:
    repo = SQLRouteRepository(db)
    return EtaUseCase(location_service, repo)


def get_route_repository(db: Session = Depends(get_db)) -> SQLRouteRepository:
    return SQLRouteRepository(db)
