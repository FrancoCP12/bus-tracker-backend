from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.location_service import LocationService, get_location_service
from typing import Optional

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.websocket("/buses/{bus_id}/location/")
async def gps_receive(
    websocket: WebSocket,
    location_service: LocationService = Depends(get_location_service),
):
    await websocket.accept()
    try:
        while True:
            bus = await websocket.receive_json()
            await location_service.set_location(bus)
    except WebSocketDisconnect:
        print("Bus desconectado")


@router.websocket("/buses/connect/{bus_id}/{company}")
async def gps_send(
    websocket: WebSocket,
    company: str,
    bus_id: str,
    location_service: LocationService = Depends(get_location_service),
):
    await websocket.accept()

    try:
        async for data in location_service.subscribe(company, bus_id):
            await websocket.send_json(data)
    except WebSocketDisconnect:
        print(f"Websocket desconectado para {bus_id} - {company}")
    except Exception as e:
        print(f"Error en la conexión: {e}")
