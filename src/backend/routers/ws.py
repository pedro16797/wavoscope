from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from backend import state

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    from utils.logging import logger

    # Send initial state
    p = state.project
    initial_loaded = p is not None
    if initial_loaded:
        await websocket.send_json({
            "position": p.position,
            "playing": p.backend._playing,
            "loop_range": p.get_loop_range(),
            "loaded": True,
            "filename": p.audio_path.name
        })
    else:
        await websocket.send_json({"loaded": False})

    last_state = {
        "position": p.position if initial_loaded else -1.0,
        "playing": p.backend._playing if initial_loaded else False,
        "loaded": initial_loaded,
        "loop_range": p.get_loop_range() if initial_loaded else None,
        "filename": p.audio_path.name if initial_loaded else None,
        "update_counter": p.update_counter if initial_loaded else 0
    }

    try:
        while True:
            p = state.project
            current_loaded = p is not None
            if current_loaded:
                pos = p.position
                playing = p.backend._playing
                filename = p.audio_path.name

                # Only send if something meaningful changed
                # Position update at ~30fps is fine during playback,
                # but if paused and not seeking, no need to spam.
                loop_range = state.project.get_loop_range()
                update_counter = state.project.update_counter
                if (playing or abs(pos - last_state.get("position", -1.0)) > 1e-4
                    or playing != last_state.get("playing")
                    or loop_range != last_state.get("loop_range")
                    or filename != last_state.get("filename")
                    or update_counter != last_state.get("update_counter")
                    or not last_state.get("loaded")):

                    if (not last_state.get("loaded")
                        or filename != last_state.get("filename")
                        or update_counter != last_state.get("update_counter")):
                        logger.info(f"WS: Project updated (loaded: {not last_state.get('loaded')}, changed: {filename != last_state.get('filename')}), sending update")

                    await websocket.send_json({
                        "position": pos,
                        "playing": playing,
                        "loop_range": loop_range,
                        "loaded": True,
                        "filename": filename,
                        "update_counter": update_counter
                    })
                    last_state["position"] = pos
                    last_state["playing"] = playing
                    last_state["loop_range"] = loop_range
                    last_state["loaded"] = True
                    last_state["filename"] = filename
                    last_state["update_counter"] = update_counter
            elif last_state.get("loaded"):
                # Project was closed
                await websocket.send_json({"loaded": False})
                last_state["loaded"] = False

            await asyncio.sleep(0.03) # 30fps update
    except WebSocketDisconnect:
        pass
