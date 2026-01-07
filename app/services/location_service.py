from dotenv import load_dotenv
import redis as r
import os

load_dotenv()
host_redis: str | None= os.getenv('HOST_REDIS')
port_redis: str | None= os.getenv('PORT_REDIS')

class BusInexist(Exception):
    """No se ha encontrado ningun bus con esa descripcion"""
    pass

if port_redis:
    port: int = int(port_redis)

class ConectionRedis():
    def __init__(self, host, port) -> None:
        self.redis = r.Redis(host = host, port= port, decode_responses= True) 
    
    def get_location(self, id = None, company = None):
        location = []
        if id:   
            location.append(self.redis.json().get(f"bus:{id}"))
        
        if company:
            for bus in self.redis.scan_iter(f'bus:{company}:*'):
                location.append(self.redis.get(bus))

        if not all(location):
            raise BusInexist()

        return location

    def set_location(self, bus):
        location = self.redis.json().set(f"bus:{bus['company']}:{bus['id']}", '$', bus)
        return location
    
redis = ConectionRedis(host_redis, port_redis)