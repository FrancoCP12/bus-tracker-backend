import redis.asyncio as redis_async
import json
import os
from typing import Any, AsyncGenerator

from app.domain.interfaces.location_service import ILocationService

REDIS_HOST = os.getenv("HOST_REDIS", "localhost")
REDIS_PORT = int(os.getenv("PORT_REDIS", 6379))


class RedisLocationService(ILocationService):
    def __init__(self, host: str = REDIS_HOST, port: int = REDIS_PORT):
        self._redis = redis_async.Redis(host=host, port=port, decode_responses=True)

    async def get_location(
        self, id_bus: str | None = None, company: str | None = None
    ) -> dict[str, Any]:
        location: dict[str, Any] = {}

        if id_bus and company:
            data = await self._redis.json().get(f"bus:{company}:{id_bus}")
            if data:
                location[id_bus] = data
        elif company:
            bus_ids = await self._redis.smembers(f"list:{company}")
            for bid in bus_ids:
                data = await self._redis.json().get(f"bus:{company}:{bid}")
                if data:
                    location[bid] = data
        else:
            list_keys = await self._redis.keys("list:*")
            for list_key in list_keys:
                comp_name = list_key.split(":")[-1]
                bus_ids = await self._redis.smembers(list_key)
                for bid in bus_ids:
                    data = await self._redis.json().get(f"bus:{comp_name}:{bid}")
                    if data:
                        location[bid] = data

        return {"type": "snapshot", "buses": location}

    async def set_location(self, bus: dict[str, Any]) -> bool:
        id_bus = bus["id"]
        company_bus = bus["company"]
        current_coord = bus["coord"]
        key = f"bus:{company_bus}:{id_bus}"

        data = bus.copy()
        data.pop("coord", None)
        data["coord"] = []

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.sadd(f"list:{company_bus}", id_bus)
            pipe.json().set(key, "$", data, nx=True)
            pipe.json().arrappend(key, "$.coord", current_coord)
            pipe.json().arrtrim(key, "$.coord", -5, -1)
            pipe.expire(key, 60)
            pipe.publish(f"canal:bus:{company_bus}:{id_bus}", json.dumps(bus))
            await pipe.execute()

        return True

    async def subscribe(
        self, company: str | None = None, id_bus: str | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        pubsub = self._redis.pubsub()

        try:
            await self.get_location(id_bus, company)

            if id_bus and company:
                await pubsub.subscribe(f"canal:bus:{company}:{id_bus}")
            elif company:
                await pubsub.psubscribe(f"canal:bus:{company}:*")
            else:
                await pubsub.psubscribe(f"canal:bus:*")

            async for msg in pubsub.listen():
                if msg["type"] in ["message", "pmessage"]:
                    yield json.loads(msg["data"])

        finally:
            await pubsub.unsubscribe()
            await pubsub.close()


_location_service: RedisLocationService | None = None

def get_location_service() -> RedisLocationService:
    global _location_service
    if _location_service is None:
        _location_service = RedisLocationService()
    return _location_service
