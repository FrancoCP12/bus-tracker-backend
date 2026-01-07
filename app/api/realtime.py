from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.location_service import redis
router = APIRouter()

@router.websocket('/buses/{id}/location/')
async def gps_receive(websockets: WebSocket):
    await websockets.accept()
    try:
        while True:
            bus = await websockets.receive_json()
            redis.set_location(bus)
            print(bus['company'])

    except WebSocketDisconnect:
        print("Bus desconectado")

