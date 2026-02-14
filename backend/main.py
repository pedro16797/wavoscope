import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Package resolution hack: Map 'wavoscope.*' to root-level modules
# This allows 'from wavoscope.audio import ...' to work when 'audio' is in the root.
import audio
import session
import utils
sys.modules["wavoscope.audio"] = audio
sys.modules["wavoscope.session"] = session
sys.modules["wavoscope.utils"] = utils

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
import threading
from typing import List, Dict, Any
from pydantic import BaseModel
import tkinter as tk
from tkinter import filedialog

from wavoscope.session.project import Project
from wavoscope.audio.spectrum_analyzer import analyze as run_fft
from wavoscope.utils.config import Config

# Global project instance (initialized on first /open)
project: Project | None = None
connected_websockets: List[WebSocket] = []

async def broadcast_position():
    while True:
        if project and project.backend._playing:
            data = json.dumps({"type": "position", "position": project.position})
            for ws in connected_websockets:
                try:
                    await ws.send_text(data)
                except Exception:
                    pass
        await asyncio.sleep(0.05) # 20 Hz update

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_position())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OpenRequest(BaseModel):
    path: str

class SeekRequest(BaseModel):
    time: float

class SpeedRequest(BaseModel):
    speed: float

class VolumeRequest(BaseModel):
    volume: float

class MetronomeRequest(BaseModel):
    enabled: bool

class FlagRequest(BaseModel):
    time: float
    type: str = "rhythm"
    subdivision: int = 0
    name: str = ""
    is_section_start: bool = False
    shaded_subdivisions: bool = False

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/browse")
async def browse():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.ogg"), ("All Files", "*.*")]
    )
    root.destroy()
    return {"path": file_path}

@app.post("/save")
async def save_project():
    if project:
        project.save()
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/open")
async def open_file(req: OpenRequest):
    global project
    path = Path(req.path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    project = Project(path)
    project.open_file(path)
    return {"status": "ok", "duration": project.duration}

@app.post("/play")
async def play():
    if project:
        project.play()
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/pause")
async def pause():
    if project:
        project.pause()
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/seek")
async def seek(req: SeekRequest):
    if project:
        project.seek(req.time)
        return {"status": "ok", "position": project.position}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/speed")
async def set_speed(req: SpeedRequest):
    if project:
        project.set_speed(req.speed)
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/volume")
async def set_volume(req: VolumeRequest):
    if project:
        project.set_volume(req.volume)
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/metronome")
async def set_metronome(req: MetronomeRequest):
    if project:
        project.backend.set_metronome_enabled(req.enabled)
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.get("/status")
async def get_status():
    if project:
        return {
            "position": project.position,
            "duration": project.duration,
            "playing": project.backend._playing,
            "speed": project.backend._speed,
            "volume": project.backend._volume
        }
    raise HTTPException(status_code=400, detail="No project open")

@app.get("/waveform")
async def get_waveform(start: float = 0, end: float = None, n: int = 2000):
    if project and project.wave_cache:
        if end is None:
            end = project.duration
        bars = project.wave_cache.bars(start, end, n)
        return {"bars": bars}
    raise HTTPException(status_code=400, detail="No project open or cache not ready")

@app.get("/spectrum")
async def get_spectrum(t: float, window: float = 0.3, low: float = 100, high: float = 5000, width: int = 1000):
    if project and project.backend._data is not None:
        freqs, db = run_fft(
            project.backend._data,
            project.backend._sr,
            t,
            window,
            low,
            high,
            width
        )
        return {
            "freqs": freqs.tolist(),
            "db": db.tolist()
        }
    raise HTTPException(status_code=400, detail="No project open or data missing")

@app.get("/flags")
async def get_flags():
    if project:
        return {"flags": project.flags}
    raise HTTPException(status_code=400, detail="No project open")

@app.post("/flags")
async def add_flag(req: FlagRequest):
    if project:
        project.add_flag(
            time=req.time,
            kind=req.type,
            subdivision=req.subdivision,
            name=req.name,
            section_start=req.is_section_start,
            shaded=req.shaded_subdivisions
        )
        return {"status": "ok"}
    raise HTTPException(status_code=400, detail="No project open")

@app.get("/themes")
async def list_themes():
    theme_dir = Path(__file__).parent.parent / "resources" / "themes"
    if not theme_dir.exists():
        return ["dark", "cosmic", "neon"]
    return [p.stem for p in theme_dir.glob("*.json")]

@app.get("/themes/{name}")
async def get_theme(name: str):
    theme_path = Path(__file__).parent.parent / "resources" / "themes" / f"{name}.json"
    if not theme_path.exists():
        raise HTTPException(status_code=404, detail="Theme not found")
    return json.loads(theme_path.read_text())

@app.get("/settings")
async def get_settings():
    cfg = Config()
    # We return a subset or just the whole thing
    return {
        "theme": cfg.get("ui.theme", "dark"),
        "click_volume": cfg.get("ui.click_volume", 0.5),
        "spectrum_keys": cfg.get("ui.spectrum_keys", 37)
    }

@app.post("/settings")
async def update_settings(data: Dict[str, Any]):
    cfg = Config()
    for k, v in data.items():
        cfg.set(f"ui.{k}", v)
    return {"status": "ok"}

@app.delete("/flags/{idx}")
async def delete_flag(idx: int):
    if project:
        if 0 <= idx < len(project.flags):
            project.remove_flag(idx)
            return {"status": "ok"}
        raise HTTPException(status_code=404, detail="Flag not found")
    raise HTTPException(status_code=400, detail="No project open")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            # We don't really expect messages from the client yet,
            # but we need to keep the connection open.
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)

# Serve frontend assets
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
