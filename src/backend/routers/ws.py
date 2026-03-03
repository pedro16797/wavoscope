from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from backend import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_state = {"position": -1.0, "playing": False}
    try:
        while True:
            if state.project:
                pos = state.project.position
                playing = state.project.backend._playing

                # Only send if something meaningful changed
                # Position update at ~30fps is fine during playback,
                # but if paused and not seeking, no need to spam.
                loop_range = state.project.get_loop_range()
                if playing or abs(pos - last_state["position"]) > 1e-4 or playing != last_state["playing"] or loop_range != last_state.get("loop_range"):
                    await websocket.send_json({
                        "position": pos,
                        "playing": playing,
                        "loop_range": loop_range
                    })
                    last_state["position"] = pos
                    last_state["playing"] = playing
                    last_state["loop_range"] = loop_range

            await asyncio.sleep(0.03) # 30fps update
    except WebSocketDisconnect:
        pass
