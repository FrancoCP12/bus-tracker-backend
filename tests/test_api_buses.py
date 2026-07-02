from app.domain.exceptions import BusAlreadyExists, BusNotFound


class TestListBuses:
    def test_list_all(self, client, mock_bus_use_case, sample_bus_response):
        mock_bus_use_case.list_buses.return_value = [sample_bus_response]
        response = client.get("/buses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["patent"] == "ABC1234"

    def test_list_with_filter(self, client, mock_bus_use_case, sample_bus_response):
        sample_bus_response["company"] = "CompanyA"
        mock_bus_use_case.list_buses.return_value = [sample_bus_response]
        response = client.get("/buses/?company=CompanyA")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["company"] == "CompanyA"


class TestCreateBus:
    def test_create_success(self, client, mock_bus_use_case, sample_bus_response):
        mock_bus_use_case.create.return_value = sample_bus_response
        response = client.post(
            "/buses/",
            json={
                "patent": "XYZ9999",
                "identifier": "BUS002",
                "company": "CompanyB",
                "is_active": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["patent"] == "ABC1234"

    def test_create_duplicate_patent(self, client, mock_bus_use_case):
        mock_bus_use_case.create.side_effect = BusAlreadyExists()
        response = client.post(
            "/buses/",
            json={
                "patent": "ABC1234",
                "identifier": "BUS001",
                "company": "CompanyA",
                "is_active": True,
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Bus already exists"


class TestUpdateBus:
    def test_update_success(self, client, mock_bus_use_case, sample_bus_response):
        mock_bus_use_case.update.return_value = sample_bus_response
        response = client.patch("/buses/1", json={"patent": "NEW1234"})
        assert response.status_code == 200

    def test_update_not_found(self, client, mock_bus_use_case):
        mock_bus_use_case.update.side_effect = BusNotFound()
        response = client.patch("/buses/999", json={"patent": "NEW1234"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Bus not found"
