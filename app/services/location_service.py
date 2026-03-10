from dotenv import load_dotenv
from fastapi import WebSocket
import redis as r
import json
import os

load_dotenv()
host_redis: str | None= os.getenv('HOST_REDIS')
port_redis: str | None= os.getenv('PORT_REDIS')

# class BusInexist(Exception):
    # """No se ha encontrado ningun bus con esa descripcion"""
    # pass

if port_redis:
    port: int = int(port_redis)

class ConectionRedis():
    def __init__(self, host, port) -> None:
        self.redis = r.Redis(host = host, port= port, decode_responses= True) 
    
    async def get_location(self, id = None, company = None, websocket = WebSocket):
        location = {}
        if id and company:
            data = self.redis.json().get(f'bus:{company}:{id}')   
            if data: location[id] = data
        
        if company:
            bus_id = self.redis.smembers(f"list:{company}")
            for bid in bus_id: # type: ignore
                data = self.redis.json().get(f"bus:{company}:{bid}")
                if data: location[bid] = data
        else:
            list_keys = self.redis.keys("list:*")
            for list_key in list_keys: # type: ignore
                comp_name = list_key.split(":")[-1] 
                bus_ids = self.redis.smembers(list_key)
                for bid in bus_ids: # type: ignore
                    data = self.redis.json().get(f"bus:{comp_name}:{bid}")
                    if data: location[bid] = data

        # if not all(location):
        #     raise BusInexist()

        await websocket.send_json({"type": "snapshot", "buses":location})  # type: ignore

        pubsub = self.redis.pubsub()
        
        if id and company:
            pubsub.subscribe(f"canal:bus:{company}:{id}")
        elif company:
            pubsub.psubscribe(f"canal:bus:{company}:*")
        else:
            pubsub.psubscribe(f"canal:bus:*")


        async for msj in pubsub.listen(): # type: ignore
            if msj["type"] == ["message", "pmessage"]:
                await websocket.send_json({"type": "update", "buses": json().loads(msj["data"])}) # type: ignore


    def set_location(self, bus):
        id_bus = bus['id']
        company_bus = bus['company']

        self.redis.sadd(f"list:{company_bus}", id_bus)
        self.redis.json().set(f"bus:{company_bus}:{id_bus}", '$', bus)

        self.redis.expire(f"bus:{company_bus}:{id_bus}", 60)

        self.redis.publish(f"canal:bus:{company_bus}:{id_bus}", json.dumps(bus))

        return True
    
redis = ConectionRedis(host_redis, port_redis)