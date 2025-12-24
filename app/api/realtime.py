from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket('/buses/{id}/location/')
async def gps_receive(websockets: WebSocket):
    await websockets.accept()
    try:
        while True:
            text = await websockets.receive_text()
            print(text)
                #guardar en redis
    except WebSocketDisconnect:
        print("Bus desconectado")

