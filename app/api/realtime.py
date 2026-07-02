import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.infrastructure.redis.location_service import RedisLocationService, get_location_service

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.websocket("/buses/{bus_id}/location/")
async def gps_receive(
    websocket: WebSocket,
    location_service: RedisLocationService = Depends(get_location_service),
):
    await websocket.accept()
    try:
        while True:
            bus = await websocket.receive_json()
            await location_service.set_location(bus)
    except WebSocketDisconnect:
        import logging
        logging.getLogger("realtime").warning("Bus disconnected")


@router.websocket("/buses/connect/{bus_id}/{company}")
async def gps_send(
    websocket: WebSocket,
    company: str,
    bus_id: str,
    location_service: RedisLocationService = Depends(get_location_service),
):
    await websocket.accept()
    try:
        async for data in location_service.subscribe(company, bus_id):
            await websocket.send_json(data)
    except WebSocketDisconnect:
        logging.getLogger("realtime").info(f"Websocket disconnected for {bus_id} - {company}")
    except Exception as e:
        logging.getLogger("realtime").error(f"Connection error: {e}")
