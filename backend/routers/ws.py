from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from backend import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if state.project:
                await websocket.send_json({
                    "position": state.project.position,
                    "playing": state.project.backend._playing
                })
            await asyncio.sleep(0.03) # 30fps update
    except WebSocketDisconnect:
        pass
