from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.location_service import redis
from typing import Optional
router = APIRouter()

@router.websocket('/buses/{id}/location/')
async def gps_receive(websockets: WebSocket):
    await websockets.accept()
    try:
        while True:
            bus = await websockets.receive_json()
            await redis.set_location(bus)
            print(bus['company'])

    except WebSocketDisconnect:
        print("Bus desconectado")

@router.websocket('/buses/connect/{id}/{company}')
async def gps_send(websocket: WebSocket, company: Optional[str]= None, id: Optional[str]= None):
    await websocket.accept()

    try:
        
        async for data in redis.subscribe(id, company): 
            await websocket.send_json(data)

    except WebSocketDisconnect:
        print(f"Websocket desconectado para {id} - {company}")

    except Exception as e:
        print(f"Error en la conexión: {e}")
