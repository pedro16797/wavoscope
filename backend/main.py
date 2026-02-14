import sys
import os
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# Fix imports for wavoscope package
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

# Mapping hack for wavoscope.*
import audio
import session
import utils
import config
sys.modules["wavoscope.audio"] = audio
sys.modules["wavoscope.session"] = session
sys.modules["wavoscope.utils"] = utils
sys.modules["wavoscope.config"] = config

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from session.project import Project

app = FastAPI()

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

project: Optional[Project] = None

class PlaybackControl(BaseModel):
    action: str
    value: Optional[float] = None

class FlagData(BaseModel):
    t: float
    type: str = "rhythm"
    subdivision: int = 0
    name: str = ""
    is_section_start: bool = False
    shaded_subdivisions: bool = False

@app.get("/status")
async def get_status():
    if not project:
        return {"loaded": False}
    return {
        "loaded": True,
        "position": project.position,
        "duration": project.duration,
        "playing": project.backend._playing,
        "speed": project.backend._speed,
        "volume": project.backend._volume,
        "filename": project.audio_path.name,
        "flags": project.flags,
        "dirty": project._dirty,
        "metronome_enabled": project.backend._metronome_enabled,
        "click_gain": project.backend._click_gain
    }

@app.post("/playback")
async def control_playback(control: PlaybackControl):
    global project
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if control.action == "play":
        project.play()
    elif control.action == "pause":
        project.pause()
    elif control.action == "stop":
        project.pause()
        if hasattr(project, "_last_play_start"):
            project.seek(project._last_play_start)
        else:
            project.seek(0)
    elif control.action == "seek":
        if control.value is not None:
            project.seek(control.value)
    elif control.action == "set_speed":
        if control.value is not None:
            project.set_speed(control.value)
    elif control.action == "set_volume":
        if control.value is not None:
            project.set_volume(control.value)

    return {"status": "ok"}

@app.get("/audio/waveform")
async def get_waveform(start: float = 0, end: float = 0, n_bars: int = 1000):
    if not project or not project.wave_cache:
        raise HTTPException(status_code=400, detail="No project or audio loaded")

    if end == 0:
        end = project.duration

    bars = project.wave_cache.bars(start, end, n_bars)
    return {"bars": bars}

@app.get("/audio/spectrum")
async def get_spectrum(position: float, window: float = 0.3, low_hz: float = 20, high_hz: float = 20000, width: int = 1000):
    if not project or project._data is None:
        raise HTTPException(status_code=400, detail="No audio loaded")

    from audio.spectrum_analyzer import analyze
    f, db = analyze(project._data, project._sr, position, window, low_hz, high_hz, width)
    return {"freqs": f.tolist(), "db": db.tolist()}

class ToneControl(BaseModel):
    freq: float = 0
    action: str = "start"

@app.post("/playback/tone")
async def play_tone(control: ToneControl):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")

    synth = project.backend._synth
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

@app.post("/playback/metronome")
async def control_metronome(control: MetronomeControl):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")

    if control.enabled is not None:
        project.backend.set_metronome_enabled(control.enabled)
    if control.gain is not None:
        project.backend.set_click_gain(control.gain)

    return {"status": "ok"}

@app.post("/project/flags")
async def add_flag(flag: FlagData):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")
    project.add_flag(
        flag.t,
        flag.type,
        flag.subdivision,
        flag.name,
        flag.is_section_start,
        flag.shaded_subdivisions
    )
    return {"status": "ok", "flags": project.flags}

@app.delete("/project/flags/{idx}")
async def remove_flag(idx: int):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")
    project.remove_flag(idx)
    return {"status": "ok", "flags": project.flags}

class FlagMove(BaseModel):
    idx: int
    t: float

@app.post("/project/flags/move")
async def move_flag(move: FlagMove):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")
    project.move_flag(move.idx, move.t)
    return {"status": "ok", "flags": project.flags}

class FlagInsertN(BaseModel):
    left_idx: int
    count: int

@app.post("/project/flags/insert_n")
async def insert_n_flags(data: FlagInsertN):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")
    project.insert_equi_spaced_flags(data.left_idx, data.left_idx + 1, data.count)
    return {"status": "ok", "flags": project.flags}

@app.post("/project/save")
async def save_project():
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")
    project.save()
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if project:
                await websocket.send_json({
                    "position": project.position,
                    "playing": project.backend._playing
                })
            await asyncio.sleep(0.03) # 30fps update
    except WebSocketDisconnect:
        pass

@app.get("/browse")
async def browse_file():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    if file_path:
        global project
        project = Project(Path(file_path))
        project.open_file(Path(file_path))
        return {"path": file_path, "status": "loaded"}
    return {"path": None}

@app.get("/themes")
async def get_themes():
    themes_dir = root_path / "resources" / "themes"
    themes = {}
    for theme_file in themes_dir.glob("*.json"):
        theme_name = theme_file.stem
        with open(theme_file, "r") as f:
            themes[theme_name] = json.load(f)
    return themes

class AppConfig(BaseModel):
    theme: Optional[str] = None
    click_volume: Optional[float] = None
    spectrum_keys: Optional[int] = None

@app.get("/config")
async def get_config():
    from utils.config import Config
    cfg = Config()
    return {
        "theme": cfg.get("ui.theme", "dark"),
        "click_volume": cfg.get("ui.click_volume", 0.3),
        "spectrum_keys": cfg.get("ui.spectrum_keys", 37)
    }

@app.post("/config")
async def update_config(new_cfg: AppConfig):
    from utils.config import Config
    cfg = Config()
    if new_cfg.theme is not None:
        cfg.set("ui.theme", new_cfg.theme)
    if new_cfg.click_volume is not None:
        cfg.set("ui.click_volume", new_cfg.click_volume)
        if project:
            project.backend.set_click_gain(new_cfg.click_volume)
    if new_cfg.spectrum_keys is not None:
        cfg.set("ui.spectrum_keys", new_cfg.spectrum_keys)
    return {"status": "ok"}

# Serve frontend if it exists
frontend_path = root_path / "frontend" / "dist"

@app.get("/")
async def read_index():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"detail": "Frontend not built. Please run 'npm run build' in frontend directory."}

if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
