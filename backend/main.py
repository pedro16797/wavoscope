from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional
import os
import sys

# Ensure wavoscope is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wavoscope.session.project import Project
from wavoscope.audio.spectrum_analyzer import analyze as run_fft

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for the current project
current_project: Optional[Project] = None

class ProjectStatus(BaseModel):
    audio_path: str
    position: float
    duration: float
    playing: bool
    speed: float
    volume: float

class Flag(BaseModel):
    t: float
    type: str
    subdivision: int
    name: str
    is_section_start: bool
    shaded_subdivisions: bool
    auto_name: Optional[str] = ""

@app.post("/load")
async def load_project(path: str):
    global current_project
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    current_project = Project(Path(path))
    current_project.open_file(Path(path))
    return {"message": f"Loaded {path}"}

@app.get("/status", response_model=ProjectStatus)
async def get_status():
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")

    return ProjectStatus(
        audio_path=str(current_project.audio_path),
        position=current_project.position,
        duration=current_project.duration,
        playing=current_project.backend._playing,
        speed=current_project.backend._speed,
        volume=current_project.backend._volume
    )

@app.post("/play")
async def play():
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.play()
    return {"message": "Playback started"}

@app.post("/pause")
async def pause():
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.pause()
    return {"message": "Playback paused"}

@app.post("/seek")
async def seek(time: float):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.seek(time)
    return {"message": f"Seeked to {time}"}

@app.post("/set_speed")
async def set_speed(speed: float):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.set_speed(speed)
    return {"message": f"Speed set to {speed}"}

@app.post("/set_volume")
async def set_volume(volume: float):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.set_volume(volume)
    return {"message": f"Volume set to {volume}"}

@app.get("/flags", response_model=List[Flag])
async def get_flags():
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    return current_project.flags

@app.post("/flags")
async def add_flag(flag: Flag):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.add_flag(
        time=flag.t,
        kind=flag.type,
        subdivision=flag.subdivision,
        name=flag.name,
        section_start=flag.is_section_start,
        shaded=flag.shaded_subdivisions
    )
    return {"message": "Flag added"}

@app.delete("/flags/{idx}")
async def remove_flag(idx: int):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    if idx < 0 or idx >= len(current_project.flags):
        raise HTTPException(status_code=404, detail="Flag index out of range")
    current_project.remove_flag(idx)
    return {"message": "Flag removed"}

@app.get("/waveform")
async def get_waveform(start: float, end: float, bars: int):
    if not current_project or not current_project.wave_cache:
        raise HTTPException(status_code=404, detail="No project or wave cache")

    data = current_project.wave_cache.bars(start, end, bars)
    return data

@app.get("/spectrum")
async def get_spectrum(time: float, window: float, low_hz: float, high_hz: float, width: int):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")

    freqs, db = run_fft(
        current_project.backend._data, current_project.backend._sr,
        time, window, low_hz, high_hz, width
    )
    return {"freqs": freqs.tolist(), "db": db.tolist()}

@app.post("/synth/start")
async def synth_start(freq: float):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.backend._synth.start_tone(freq)
    return {"message": f"Tone started: {freq} Hz"}

@app.post("/synth/stop")
async def synth_stop(freq: float):
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.backend._synth.stop_tone(freq)
    return {"message": f"Tone stopped: {freq} Hz"}

@app.post("/synth/stop_all")
async def synth_stop_all():
    if not current_project:
        raise HTTPException(status_code=404, detail="No project loaded")
    current_project.backend._synth.stop_all()
    return {"message": "All tones stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
