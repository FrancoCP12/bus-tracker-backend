from dotenv import load_dotenv
import redis.asyncio as r
import json
import os
from typing import Any, AsyncGenerator

load_dotenv()

HOST_REDIS = os.getenv('HOST_REDIS', 'localhost')
PORT_REDIS = int(os.getenv('PORT_REDIS', 6379))


class ConnectionRedis:
    """
    Gestor de conexiones Redis para tracking en tiempo real.
    
    Maneja almacenamiento y suscripción de ubicaciones GPS
    de autobuses usando Redis pub/sub y JSON.
    """
    
    def __init__(self, host: str, port: int):
        self.redis = r.Redis(host=host, port=port, decode_responses=True)

    async def get_location(
        self,
        id_bus: str | None = None,
        company: str | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Obtiene ubicaciones almacenadas de autobuses.
        
        Args:
            id_bus: Filtrar por ID específico (opcional)
            company: Filtrar por empresa (opcional)
            
        Yields:
            Dict con snapshot de ubicaciones
        """
        location: dict[str, Any] = {}
        
        if id_bus and company:
            data = await self.redis.json().get(f'bus:{company}:{id_bus}')
            if data:
                location[id_bus] = data

        elif company:
            bus_ids = await self.redis.smembers(f"list:{company}")
            for bid in bus_ids:
                data = await self.redis.json().get(f"bus:{company}:{bid}")
                if data:
                    location[bid] = data
                    
        else:
            list_keys = await self.redis.keys("list:*")
            for list_key in list_keys:
                comp_name = list_key.split(":")[-1]
                bus_ids = await self.redis.smembers(list_key)
                for bid in bus_ids:
                    data = await self.redis.json().get(f"bus:{comp_name}:{bid}")
                    if data:
                        location[bid] = data

        yield {"type": "snapshot", "buses": location}

    async def set_location(self, bus: dict[str, Any]) -> bool:
        """
        Almacena ubicación de autobús en Redis.
        
        Guarda en JSON, mantiene historial de últimas 5 coordenadas,
        y publica actualización para suscriptores.
        
        Args:
            bus: Dict con id, company, coord
            
        Returns:
            True si se guardó correctamente
        """
        id_bus = bus['id']
        company_bus = bus['company']
        current_coord = bus["coord"]
        key = f"bus:{company_bus}:{id_bus}"

        data = bus.copy()
        data.pop("coord", None)
        data["coord"] = []

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.sadd(f"list:{company_bus}", id_bus)
            pipe.json().set(key, '$', data, nx=True)
            pipe.json().arrappend(key, "$.coord", current_coord)
            pipe.json().arrtrim(key, "$.coord", -5, -1)
            pipe.expire(key, 60)
            pipe.publish(f"canal:bus:{company_bus}:{id_bus}", json.dumps(bus))
            await pipe.execute()

        return True

    async def subscribe(
        self,
        company: str | None = None,
        id_bus: str | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Suscribe a actualizaciones de ubicación en tiempo real.
        
        Args:
            company: Filtrar por empresa (opcional)
            id_bus: Filtrar por ID específico (opcional)
            
        Yields:
            Dict con actualización de autobús
        """
        pubsub = self.redis.pubsub()
        
        try:
            async for _ in self.get_location(id_bus, company):
                pass
            
            if id_bus and company:
                await pubsub.subscribe(f"canal:bus:{company}:{id_bus}")
            elif company:
                await pubsub.psubscribe(f"canal:bus:{company}:*")
            else:
                await pubsub.psubscribe(f"canal:bus:*")

            async for msg in pubsub.listen():
                if msg["type"] in ["message", "pmessage"]:
                    yield {"type": "update", "buses": json.loads(msg["data"])}
                    
        finally:
            await pubsub.unsubscribe()
            await pubsub.close()


redis = ConnectionRedis(HOST_REDIS, PORT_REDIS)
