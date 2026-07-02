import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.redis.location_service import RedisLocationService as LocationService


@pytest.fixture
def location_service():
    return LocationService(host="localhost", port=6379)


@pytest.mark.asyncio
class TestLocationService:
    async def test_get_location_by_id_and_company(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        mock_redis.json.return_value.get = AsyncMock(
            return_value={"coord": [[-34.0, -58.0, 100.0]]}
        )
        result = await location_service.get_location(id_bus="1", company="CompanyA")
        assert result["type"] == "snapshot"
        assert "1" in result["buses"]

    async def test_get_location_by_company_only(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        mock_redis.smembers = AsyncMock(return_value={"1", "2"})
        mock_redis.json.return_value.get = AsyncMock(
            return_value={"coord": [[-34.0, -58.0, 100.0]]}
        )
        result = await location_service.get_location(company="CompanyA")
        assert result["type"] == "snapshot"

    async def test_get_location_no_filters(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        mock_redis.keys = AsyncMock(return_value=["list:CompanyA"])
        mock_redis.smembers = AsyncMock(return_value={"1"})
        mock_redis.json.return_value.get = AsyncMock(
            return_value={"coord": [[-34.0, -58.0, 100.0]]}
        )
        result = await location_service.get_location()
        assert result["type"] == "snapshot"

    async def test_get_location_no_data(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        mock_redis.json.return_value.get = AsyncMock(return_value=None)
        result = await location_service.get_location(id_bus="1", company="CompanyA")
        assert result == {"type": "snapshot", "buses": {}}

    async def test_set_location(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        pipe = MagicMock()
        pipe.__aenter__.return_value = pipe
        pipe.execute = AsyncMock()
        pipe.json = MagicMock()
        mock_redis.pipeline.return_value = pipe
        bus_data = {"id": "1", "company": "CompanyA", "coord": [-34.0, -58.0, 100.0]}
        result = await location_service.set_location(bus_data)
        assert result is True
        pipe.execute.assert_awaited_once()

    async def test_set_location_without_coord(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        pipe = MagicMock()
        pipe.__aenter__.return_value = pipe
        pipe.execute = AsyncMock()
        pipe.json = MagicMock()
        mock_redis.pipeline.return_value = pipe
        bus_data = {"id": "2", "company": "CompanyB", "coord": [-35.0, -59.0, 200.0]}
        result = await location_service.set_location(bus_data)
        assert result is True

    async def test_subscribe_id_and_company(self, location_service):
        mock_redis = MagicMock()
        location_service._redis = mock_redis
        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.listen.return_value.__aiter__.return_value = [
            {"type": "message", "data": '{"id":"1","coord":[-34.0,-58.0]}'}
        ]
        mock_redis.pubsub.return_value = mock_pubsub
        mock_redis.json.return_value.get = AsyncMock(return_value={})
        messages = []
        async for msg in location_service.subscribe("CompanyA", "1"):
            messages.append(msg)
            break
        assert len(messages) == 1
        assert messages[0]["id"] == "1"
