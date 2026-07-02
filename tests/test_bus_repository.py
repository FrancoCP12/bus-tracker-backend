from unittest.mock import MagicMock
from app.infrastructure.repositories.sqlalchemy.bus_repository import SQLBusRepository
from app.domain.entities.bus import Bus
from app.domain.value_objects import BusFilter
from app.models.bus import Bus as BusModel


class TestSQLBusRepository:
    def setup_repo(self, mock_db):
        repo = SQLBusRepository(mock_db)
        return repo

    def test_get_by_id_found(self, mock_db):
        mock_result = MagicMock(spec=BusModel)
        mock_result.id_bus = 1
        mock_result.id_route = 1
        mock_result.patent = "ABC1234"
        mock_result.identifier = "BUS001"
        mock_result.company = "CompanyA"
        mock_result.is_active = True

        mock_db.query.return_value.filter.return_value.first.return_value = mock_result
        repo = self.setup_repo(mock_db)
        result = repo.get_by_id(1)
        assert result is not None
        assert result.id_bus == 1
        assert result.patent == "ABC1234"

    def test_get_by_id_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        repo = self.setup_repo(mock_db)
        result = repo.get_by_id(999)
        assert result is None

    def test_get_all_no_filters(self, mock_db):
        mock_result = MagicMock(spec=BusModel)
        mock_result.id_bus = 1
        mock_result.patent = "ABC1234"
        mock_result.identifier = "BUS001"
        mock_result.company = "CompanyA"
        mock_result.is_active = True
        mock_db.query.return_value.all.return_value = [mock_result]
        repo = self.setup_repo(mock_db)
        result = repo.get_all()
        assert len(result) == 1
        assert result[0].patent == "ABC1234"

    def test_get_all_with_id_filter(self, mock_db):
        mock_result = MagicMock(spec=BusModel)
        mock_result.id_bus = 1
        mock_result.patent = "ABC1234"
        mock_result.identifier = "BUS001"
        mock_result.company = "CompanyA"
        mock_result.is_active = True
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_result]
        repo = self.setup_repo(mock_db)
        result = repo.get_all(BusFilter(id=1))
        assert len(result) == 1

    def test_get_by_patent_found(self, mock_db):
        mock_result = MagicMock(spec=BusModel)
        mock_result.id_bus = 1
        mock_result.patent = "ABC1234"
        mock_result.identifier = "BUS001"
        mock_result.company = "CompanyA"
        mock_result.is_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_result
        repo = self.setup_repo(mock_db)
        result = repo.get_by_patent("ABC1234")
        assert result is not None
