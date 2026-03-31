from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from backend import state
from utils.logging import logger
from session.project import Project

router = APIRouter(prefix="/playback", tags=["playback"])

class PlaybackControl(BaseModel):
    action: str
    value: Optional[float] = None

def trigger_next_playlist_item():
    if not state.active_playlist_id or not state.active_item_id:
        return

    playlist = state.playlist_manager.get_playlist(state.active_playlist_id)
    if not playlist or not playlist.items:
        return

    # Keep track of current loop mode to carry it over
    old_loop_mode = state.project.loop_mode if state.project else "none"

    # Try items until one exists or we've tried them all
    current_item_id = state.active_item_id
    tried_count = 0
    while tried_count < len(playlist.items):
        next_item = state.playlist_manager.get_next_item(state.active_playlist_id, current_item_id)
        if not next_item:
            break

        path = Path(next_item.path)
        if path.exists():
            try:
                if state.project:
                    state.project.close()

                new_project = Project(path)
                new_project.open_file(path)
                state.project = new_project
                state.active_item_id = next_item.id

                # Re-register callback for the next transition
                if hasattr(state, 'on_playback_finished'):
                    state.project.backend.register_callback("finished", state.on_playback_finished)

                # Carry over the playlist loop mode
                state.project.set_loop_mode(old_loop_mode)

                state.project.play()
                return
            except Exception as e:
                logger.error(f"Failed to open next playlist item {path}: {e}")
        else:
            logger.warning(f"Playlist item {next_item.path} not found, skipping...")

        current_item_id = next_item.id
        tried_count += 1

    logger.error("No valid items found in playlist to auto-advance.")

@router.post("")
async def control_playback(control: PlaybackControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        if control.action == "play":
            state.project.play()
        elif control.action == "pause":
            state.project.pause()
        elif control.action == "stop":
            state.project.pause()
            if hasattr(state.project, "_last_play_start"):
                state.project.seek(state.project._last_play_start)
            else:
                state.project.seek(0)
        elif control.action == "seek":
            if control.value is not None:
                state.project.seek(control.value)
        elif control.action == "next":
            trigger_next_playlist_item()
        elif control.action == "prev":
            if state.active_playlist_id and state.active_item_id:
                playlist = state.playlist_manager.get_playlist(state.active_playlist_id)
                if not playlist: return

                old_loop_mode = state.project.loop_mode if state.project else "none"
                current_item_id = state.active_item_id
                tried_count = 0
                while tried_count < len(playlist.items):
                    prev_item = state.playlist_manager.get_prev_item(state.active_playlist_id, current_item_id)
                    if not prev_item: break

                    path = Path(prev_item.path)
                    if path.exists():
                        if state.project: state.project.close()
                        new_project = Project(path)
                        new_project.open_file(path)
                        state.project = new_project
                        state.active_item_id = prev_item.id

                        if hasattr(state, 'on_playback_finished'):
                            state.project.backend.register_callback("finished", state.on_playback_finished)
                        state.project.set_loop_mode(old_loop_mode)
                        state.project.play()
                        break
                    current_item_id = prev_item.id
                    tried_count += 1
        elif control.action == "set_speed":
            if control.value is not None:
                state.project.set_speed(control.value)
        elif control.action == "set_volume":
            if control.value is not None:
                state.project.set_volume(control.value)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown playback action: {control.action}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Playback control error: {str(e)}")

    return {"status": "ok"}

class ToneControl(BaseModel):
    freq: float = 0
    freqs: Optional[List[float]] = None
    action: str = "start"
    stop_others: bool = False

@router.post("/tone")
async def play_tone(control: ToneControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        synth = state.project.backend._synth
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tone generation error: {str(e)}")

    return {"status": "ok"}

class MetronomeControl(BaseModel):
    enabled: Optional[bool] = None
    volume: Optional[float] = None

@router.post("/metronome")
async def control_metronome(control: MetronomeControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        if control.enabled is not None:
            state.project.backend.set_metronome_enabled(control.enabled)
        if control.volume is not None:
            state.project.backend.set_click_volume(control.volume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metronome control error: {str(e)}")

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
async def control_loop(control: LoopControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        state.project.set_loop_mode(control.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loop control error: {str(e)}")

    return {"status": "ok", "loop_mode": state.project.loop_mode}

@router.post("/filter")
async def control_filter(control: FilterControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        state.project.backend.set_filter(
            enabled=control.enabled,
            low=control.low_hz,
            high=control.high_hz,
            low_enabled=control.low_enabled,
            high_enabled=control.high_enabled,
            auto_gain=control.auto_gain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter control error: {str(e)}")

    return {"status": "ok"}
