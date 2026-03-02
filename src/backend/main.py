import sys
from pathlib import Path

# Fix imports for wavoscope package
src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path))
root_path = src_path.parent

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

from backend import state  # noqa: E402
from backend.routers import playback, audio, project, config, themes, ws, locales  # noqa: E402
from backend import autosave  # noqa: E402
from utils.logging import logger # noqa: E402

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    autosave.start()

@app.on_event("shutdown")
async def shutdown_event():
    autosave.stop()

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
app.include_router(locales.router)

# Serve locales
locales_path = root_path / "resources" / "locales"
if locales_path.exists():
    app.mount("/locales", StaticFiles(directory=str(locales_path)), name="locales")

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
        "metadata": state.project.metadata,
        "flags": state.project.flags,
        "harmony_flags": state.project.harmony_flags,
        "lyrics": state.project.lyrics,
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
frontend_path = src_path / "frontend" / "dist"

@app.get("/")
async def read_index():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"detail": "Frontend not built. Please run 'npm run build' in frontend directory."}

if frontend_path.exists():
    # Serve static files from frontend/dist
    # We mount it at / so that favicons and other root files are accessible
    # Note: app.mount("/") should be added after all other routes to avoid overriding them
    app.mount("/", StaticFiles(directory=str(frontend_path)), name="frontend")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
