import sys
from pathlib import Path

# Fix imports for wavoscope package
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from backend import state  # noqa: E402
from backend.routers import playback, audio, project, config, themes, ws  # noqa: E402

app = FastAPI()

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular routers
app.include_router(playback.router)
app.include_router(audio.router)
app.include_router(project.router)
app.include_router(config.router)
app.include_router(themes.router)
app.include_router(ws.router)

@app.get("/status")
async def get_status():
    if not state.project:
        return {"loaded": False}
    return {
        "loaded": True,
        "position": state.project.position,
        "duration": state.project.duration,
        "playing": state.project.backend._playing,
        "speed": state.project.backend._speed,
        "volume": state.project.backend._volume,
        "filename": state.project.audio_path.name,
        "flags": state.project.flags,
        "harmony_flags": state.project.harmony_flags,
        "time_signature": state.project.time_signature,
        "dirty": state.project._dirty,
        "metronome_enabled": state.project.backend._metronome_enabled,
        "click_volume": state.project.backend._click_volume,
        "loop_mode": state.project.loop_mode,
        "loop_range": state.project.get_loop_range(),
        "filter_enabled": state.project.backend._filter_enabled,
        "filter_low_enabled": state.project.backend._filter_low_enabled,
        "filter_high_enabled": state.project.backend._filter_high_enabled,
        "filter_low_hz": state.project.backend._filter_low_hz,
        "filter_high_hz": state.project.backend._filter_high_hz,
    }

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
    print("[Backend] Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
