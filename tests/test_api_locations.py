class TestSearchBus:
    def test_search_success(self, client, mock_route_use_case):
        mock_route_use_case.search_buses.return_value = []
        response = client.post(
            "/locations/search/?lat_origin=-34.0&lon_origin=-58.0&lat_dest=-34.1&lon_dest=-58.1"
        )
        assert response.status_code == 200

    def test_search_no_results(self, client, mock_route_use_case):
        mock_route_use_case.search_buses.return_value = []
        response = client.post(
            "/locations/search/?lat_origin=-34.0&lon_origin=-58.0&lat_dest=-34.1&lon_dest=-58.1"
        )
        assert response.status_code == 200
        assert response.json() == []
