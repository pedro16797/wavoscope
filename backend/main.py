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
import gui
sys.modules["wavoscope.audio"] = audio
sys.modules["wavoscope.session"] = session
sys.modules["wavoscope.utils"] = utils
sys.modules["wavoscope.config"] = config
sys.modules["wavoscope.gui"] = gui

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
        "flags": project.flags
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

@app.post("/playback/tone")
async def play_tone(freq: float = 0, action: str = "start"):
    if not project:
        raise HTTPException(status_code=400, detail="No project loaded")

    synth = project.backend._synth
    if action == "start":
        synth.start_tone(freq)
    elif action == "stop":
        if freq == 0:
            synth.stop_all()
        else:
            synth.stop_tone(freq)
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
    themes_dir = root_path / "gui" / "themes"
    themes = {}
    for theme_file in themes_dir.glob("*.json"):
        theme_name = theme_file.stem
        with open(theme_file, "r") as f:
            themes[theme_name] = json.load(f)
    return themes

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
