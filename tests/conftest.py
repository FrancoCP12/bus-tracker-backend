from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.main import app
from fastapi.testclient import TestClient

from app.use_cases.bus import BusUseCase
from app.use_cases.eta import EtaUseCase
from app.use_cases.route import RouteUseCase


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_bus_use_case():
    uc = MagicMock(spec=BusUseCase)
    return uc


@pytest.fixture
def mock_route_use_case():
    uc = MagicMock(spec=RouteUseCase)
    return uc


@pytest.fixture
def mock_eta_use_case():
    uc = MagicMock(spec=EtaUseCase)
    return uc


@pytest.fixture
def override_deps(mock_bus_use_case, mock_route_use_case, mock_eta_use_case):
    from app.api.dependencies import get_bus_use_case, get_route_use_case, get_eta_use_case
    app.dependency_overrides[get_bus_use_case] = lambda: mock_bus_use_case
    app.dependency_overrides[get_route_use_case] = lambda: mock_route_use_case
    app.dependency_overrides[get_eta_use_case] = lambda: mock_eta_use_case
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_deps):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_bus():
    from app.models.bus import Bus
    return Bus(
        id_bus=1,
        id_route=1,
        patent="ABC1234",
        identifier="BUS001",
        company="CompanyA",
        is_active=True,
    )


@pytest.fixture
def sample_bus_response():
    return {
        "id_bus": 1,
        "id_route": 1,
        "patent": "ABC1234",
        "identifier": "BUS001",
        "company": "CompanyA",
        "is_active": True,
    }
