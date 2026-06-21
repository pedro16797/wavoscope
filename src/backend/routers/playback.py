from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from backend import state
from backend.deps import require_project
from utils.logging import logger
from session.project import Project

router = APIRouter(prefix="/playback", tags=["playback"])

class PlaybackControl(BaseModel):
    action: str
    value: Optional[float] = None

def _advance_playlist(direction: int) -> None:
    """Switch playback to the next (direction >= 0) or previous playlist item,
    skipping any items whose files are missing."""
    if not state.active_playlist_id or not state.active_item_id:
        return

    playlist = state.playlist_manager.get_playlist(state.active_playlist_id)
    if not playlist or not playlist.items:
        return

    get_item = (state.playlist_manager.get_next_item if direction >= 0
                else state.playlist_manager.get_prev_item)

    # Hold the swap lock for the whole advance so it can't interleave with a
    # route-driven open / next / prev (which would clobber state or close a
    # just-opened project). Uncontended in the common case, so no added latency.
    with state.project_lock:
        # Carry over the current loop mode to the new track.
        old_loop_mode = state.project.loop_mode if state.project else "none"
        current_item_id = state.active_item_id

        for _ in range(len(playlist.items)):
            item = get_item(state.active_playlist_id, current_item_id)
            if not item:
                break

            path = Path(item.path)
            if path.exists():
                new_project = None
                swapped = False
                try:
                    new_project = Project(path)
                    new_project.open_file(path)

                    # Re-register callback for the next transition.
                    if state.on_playback_finished:
                        new_project.backend.register_callback("finished", state.on_playback_finished)

                    new_project.set_loop_mode(old_loop_mode)

                    # Atomically swap in the new project and close the previous one.
                    state.set_project(new_project)
                    swapped = True
                    state.active_item_id = item.id
                    new_project.play()
                    return
                except Exception as e:
                    logger.error(f"Failed to open playlist item {path}: {e}")
                    # Only close the new project here if we failed before it
                    # became the active project. After the swap it's owned by
                    # state and will be closed by the next set_project.
                    if new_project is not None and not swapped:
                        new_project.close()
            else:
                logger.warning(f"Playlist item {item.path} not found, skipping...")

            current_item_id = item.id

        logger.error("No valid items found in playlist to advance.")

def trigger_next_playlist_item():
    _advance_playlist(1)

@router.post("")
async def control_playback(control: PlaybackControl, project: Project = Depends(require_project)):
    if control.action == "play":
        project.play()
    elif control.action == "pause":
        project.pause()
    elif control.action == "stop":
        project.pause()
        project.seek(0)
    elif control.action == "seek":
        if control.value is not None:
            project.seek(control.value)
    elif control.action == "next":
        _advance_playlist(1)
    elif control.action == "prev":
        _advance_playlist(-1)
    elif control.action == "set_speed":
        if control.value is not None:
            project.set_speed(control.value)
    elif control.action == "set_volume":
        if control.value is not None:
            project.set_volume(control.value)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown playback action: {control.action}")

    return {"status": "ok"}

class ToneControl(BaseModel):
    freq: float = 0
    freqs: Optional[List[float]] = None
    action: str = "start"
    stop_others: bool = False

@router.post("/tone")
async def play_tone(control: ToneControl, project: Project = Depends(require_project)):
    synth = project.backend._synth
    if control.stop_others:
        synth.stop_all()

    if control.action == "start":
        if control.freqs:
            for f in control.freqs:
                synth.start_tone(f)
        else:
            synth.start_tone(control.freq)
    elif control.action == "stop":
        if control.freqs:
            for f in control.freqs:
                synth.stop_tone(f)
        elif control.freq == 0:
            synth.stop_all()
        else:
            synth.stop_tone(control.freq)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tone action: {control.action}")

    return {"status": "ok"}

class MetronomeControl(BaseModel):
    enabled: Optional[bool] = None
    volume: Optional[float] = None

@router.post("/metronome")
async def control_metronome(control: MetronomeControl, project: Project = Depends(require_project)):
    if control.enabled is not None:
        project.backend.set_metronome_enabled(control.enabled)
    if control.volume is not None:
        project.backend.set_click_volume(control.volume)
    return {"status": "ok"}

class LoopControl(BaseModel):
    mode: str

class FilterControl(BaseModel):
    enabled: Optional[bool] = None
    low_hz: Optional[float] = None
    high_hz: Optional[float] = None
    low_enabled: Optional[bool] = None
    high_enabled: Optional[bool] = None
    auto_gain: Optional[bool] = None

@router.post("/loop")
async def control_loop(control: LoopControl, project: Project = Depends(require_project)):
    project.set_loop_mode(control.mode)
    return {"status": "ok", "loop_mode": project.loop_mode}

@router.post("/filter")
async def control_filter(control: FilterControl, project: Project = Depends(require_project)):
    project.backend.set_filter(
        enabled=control.enabled,
        low=control.low_hz,
        high=control.high_hz,
        low_enabled=control.low_enabled,
        high_enabled=control.high_enabled,
        auto_gain=control.auto_gain
    )
    return {"status": "ok"}
