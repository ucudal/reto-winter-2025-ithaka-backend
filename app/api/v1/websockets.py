from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.websockets.handlers import handle_user_message
from app.websockets.manager import WebSocketManager

router = APIRouter()


@router.websocket("/")
async def chat_websocket(websocket: WebSocket):
    manager = WebSocketManager()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await handle_user_message(websocket, data, manager)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
