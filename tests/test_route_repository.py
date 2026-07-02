import pytest
import json
from unittest.mock import MagicMock, patch
from app.infrastructure.repositories.sqlalchemy.route_repository import SQLRouteRepository
from app.domain.exceptions import InvalidGeoJson
from app.models.route import Route as RouteModel
from app.models.bus_stop import BusStop as BusStopModel


SAMPLE_GEOJSON = json.dumps({
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"type": "route"},
            "geometry": {
                "type": "LineString",
                "coordinates": [[-58.0, -34.0], [-58.1, -34.1]],
            },
        },
        {
            "type": "Feature",
            "properties": {"type": "bus_stop"},
            "geometry": {"type": "Point", "coordinates": [-58.05, -34.05]},
        },
    ],
})


class TestSQLRouteRepository:
    def setup_repo(self, mock_db):
        return SQLRouteRepository(mock_db)

    def test_no_route_feature_raises_error(self, mock_db):
        geojson_no_route = json.dumps({
            "type": "FeatureCollection", "features": []
        })
        repo = self.setup_repo(mock_db)
        with pytest.raises(InvalidGeoJson):
            repo.create_route_from_geojson(geojson_no_route, 1)

    def test_successful_route_creation(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,
            MagicMock(spec=BusStopModel),
        ]
        repo = self.setup_repo(mock_db)
        result = repo.create_route_from_geojson(SAMPLE_GEOJSON, 1)
        assert result == {"message": "Ruta y paradas procesadas correctamente"}
        mock_db.add.assert_called()
        mock_db.flush.assert_called()
        mock_db.commit.assert_called()

    def test_get_stops_near_returns_list(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []
        repo = self.setup_repo(mock_db)
        result = repo.get_stops_near(-34.0, -58.0)
        assert result == []

    def test_get_bus_ids_by_stop(self, mock_db):
        mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [(1,), (2,)]
        repo = self.setup_repo(mock_db)
        result = repo.get_bus_ids_by_stop(1)
        assert result == [1, 2]
