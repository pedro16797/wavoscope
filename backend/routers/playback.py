from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend import state

router = APIRouter(prefix="/playback", tags=["playback"])

class PlaybackControl(BaseModel):
    action: str
    value: Optional[float] = None

@router.post("")
async def control_playback(control: PlaybackControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

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
    elif control.action == "set_speed":
        if control.value is not None:
            state.project.set_speed(control.value)
    elif control.action == "set_volume":
        if control.value is not None:
            state.project.set_volume(control.value)

    return {"status": "ok"}

class ToneControl(BaseModel):
    freq: float = 0
    action: str = "start"

@router.post("/tone")
async def play_tone(control: ToneControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    synth = state.project.backend._synth
    if control.action == "start":
        synth.start_tone(control.freq)
    elif control.action == "stop":
        if control.freq == 0:
            synth.stop_all()
        else:
            synth.stop_tone(control.freq)
    return {"status": "ok"}

class MetronomeControl(BaseModel):
    enabled: Optional[bool] = None
    gain: Optional[float] = None

@router.post("/metronome")
async def control_metronome(control: MetronomeControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if control.enabled is not None:
        state.project.backend.set_metronome_enabled(control.enabled)
    if control.gain is not None:
        state.project.backend.set_click_gain(control.gain)

    return {"status": "ok"}

class LoopControl(BaseModel):
    mode: str

@router.post("/loop")
async def control_loop(control: LoopControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    state.project.set_loop_mode(control.mode)
    return {"status": "ok", "loop_mode": state.project.loop_mode}
