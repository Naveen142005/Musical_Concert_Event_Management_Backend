from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

connected_admins: List[WebSocket] = []

async def notify_admins(message: dict):
    disconnected = []
    for ws in connected_admins:
        try:
            await ws.send_json(message)
        except WebSocketDisconnect:
            disconnected.append(ws)
    for ws in disconnected:
        connected_admins.remove(ws)

@router.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    connected_admins.append(websocket)
    try:
        while True:
            data = await websocket.receive_text() 
    except WebSocketDisconnect:
        connected_admins.remove(websocket)
