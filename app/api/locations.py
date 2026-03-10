from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.location_service import redis
router = APIRouter()

class SearchBy():
    def __init__(
            
    ):
    
#CAMBIAR ESTO TENEMOS Q HACER UNA SUSCRIPCION PUB/SUB DE REDIS CON WEBSOCKET PARA Q EL CLIENTE SOLO SE SUSCRIBA AL CHANNEL
@router.get('/location/')
def getLocation(filter: SearchBy = Depends(SearchBy)):
    pass
