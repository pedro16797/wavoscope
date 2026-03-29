from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from backend import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Send initial state
    initial_loaded = state.project is not None
    if initial_loaded:
        await websocket.send_json({
            "position": state.project.position,
            "playing": state.project.backend._playing,
            "loop_range": state.project.get_loop_range(),
            "loaded": True
        })
    else:
        await websocket.send_json({"loaded": False})

    last_state = {
        "position": state.project.position if initial_loaded else -1.0,
        "playing": state.project.backend._playing if initial_loaded else False,
        "loaded": initial_loaded,
        "loop_range": state.project.get_loop_range() if initial_loaded else None
    }

    try:
        while True:
            current_loaded = state.project is not None
            if current_loaded:
                from utils.logging import logger
                pos = state.project.position
                playing = state.project.backend._playing

                # Only send if something meaningful changed
                # Position update at ~30fps is fine during playback,
                # but if paused and not seeking, no need to spam.
                loop_range = state.project.get_loop_range()
                if (playing or abs(pos - last_state.get("position", -1.0)) > 1e-4
                    or playing != last_state.get("playing")
                    or loop_range != last_state.get("loop_range")
                    or not last_state.get("loaded")):

                    if not last_state.get("loaded"):
                        logger.info("WS: Project detected as loaded, sending update")

                    await websocket.send_json({
                        "position": pos,
                        "playing": playing,
                        "loop_range": loop_range,
                        "loaded": True
                    })
                    last_state["position"] = pos
                    last_state["playing"] = playing
                    last_state["loop_range"] = loop_range
                    last_state["loaded"] = True
            elif last_state.get("loaded"):
                # Project was closed
                await websocket.send_json({"loaded": False})
                last_state["loaded"] = False

            await asyncio.sleep(0.03) # 30fps update
    except WebSocketDisconnect:
        pass
