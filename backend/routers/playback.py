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
    action: str = "start"

@router.post("/tone")
async def play_tone(control: ToneControl):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    try:
        synth = state.project.backend._synth
        if control.action == "start":
            synth.start_tone(control.freq)
        elif control.action == "stop":
            if control.freq == 0:
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
            state.project.backend.set_click_gain(control.volume)
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
            high_enabled=control.high_enabled
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter control error: {str(e)}")

    return {"status": "ok"}
