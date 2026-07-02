import json


class TestStoreRoute:
    def test_store_route_success(self, client, mock_route_use_case):
        mock_route_use_case.create_from_geojson.return_value = {
            "message": "Ruta y paradas procesadas correctamente"
        }
        geojson = json.dumps({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"type": "route"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[-58.0, -34.0], [-58.1, -34.1]],
                    },
                }
            ],
        })
        response = client.post("/routes/geojson/", params={"geojson": geojson, "bus_id": 1})
        assert response.status_code == 200


class TestGetBusStops:
    def test_get_bus_stops(self, client, mock_route_use_case):
        mock_route_use_case.get_stops_near.return_value = []
        response = client.get("/routes/bus-stop/-34.0/-58.0")
        assert response.status_code == 200
        assert response.json() == []


class TestGetEta:
    def test_eta_no_params_returns_400(self, client, mock_eta_use_case):
        from app.domain.exceptions import InvalidParameters
        mock_eta_use_case.calculate.side_effect = InvalidParameters()
        response = client.get("/routes/buses/eta/")
        assert response.status_code == 400
