import sys
from pathlib import Path

# Fix imports for wavoscope package
src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path))
root_path = src_path.parent

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402

from backend import state  # noqa: E402
from backend.routers import (  # noqa: E402
    playback,
    audio,
    project,
    config,
    themes,
    ws,
    locales,
    playlists,
)
from backend import autosave  # noqa: E402
from utils.logging import logger # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    autosave.start()

    def on_playback_finished():
        if state.project and state.project.loop_mode == "playlist":
            from backend.routers.playback import trigger_next_playlist_item
            trigger_next_playlist_item()

    # Registered per-project on load (the active project can change over time).
    state.on_playback_finished = on_playback_finished

    yield

    autosave.stop()


app = FastAPI(lifespan=lifespan)

# The packaged app and remote devices load the UI from the backend itself
# (same-origin, not subject to CORS), so the only legitimate cross-origin caller
# is the Vite dev server. Restrict to those origins instead of "*" so a
# malicious page in the host's browser can't drive the local API.
_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Last-resort handler so unexpected errors become a clean 500 (and are logged
    with the offending route) instead of being wrapped by hand in every endpoint."""
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    # This handler runs in ServerErrorMiddleware, outside CORSMiddleware, so echo
    # the CORS header here for allowed origins — otherwise a dev-server 500 shows
    # up in the browser as an opaque CORS failure instead of the actual error.
    headers = {}
    origin = request.headers.get("origin")
    if origin in _DEV_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
    return JSONResponse(status_code=500, content={"detail": "Internal server error"}, headers=headers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEV_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Content / control / settings endpoints. Static frontend assets, the index,
# and non-sensitive UI resources (/themes, /locales) stay public so a remote
# browser can load the app shell; the app then attaches the remote token to
# these API calls. Loopback is always authorized, so this only affects the
# remote-access-enabled deployment (which was previously fully open).
_GATED_PREFIXES = ("/status", "/playback", "/audio", "/project", "/config", "/playlists")


@app.middleware("http")
async def remote_authorization(request: Request, call_next):
    from backend.deps import is_authorized_request

    # Let CORS preflight through (it carries no token by design).
    if request.method != "OPTIONS":
        path = request.url.path
        if any(path == p or path.startswith(p + "/") for p in _GATED_PREFIXES):
            if not is_authorized_request(request):
                headers = {}
                origin = request.headers.get("origin")
                if origin in _DEV_ORIGINS:
                    headers["Access-Control-Allow-Origin"] = origin
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Remote access requires a valid token"},
                    headers=headers,
                )
    return await call_next(request)

# Include modular routers
app.include_router(playback.router)
app.include_router(audio.router)
app.include_router(project.router)
app.include_router(config.router)
app.include_router(themes.router)
app.include_router(ws.router)
app.include_router(locales.router)
app.include_router(playlists.router)

# Serve locales
locales_path = root_path / "resources" / "locales"
if locales_path.exists():
    app.mount("/locales", StaticFiles(directory=str(locales_path)), name="locales")

@app.get("/status")
async def get_status():
    # Snapshot the active project once: a concurrent playlist auto-advance or
    # /project/open can swap state.project out from under us mid-build, which
    # would otherwise NPE partway through this dict.
    p = state.project
    if p is None:
        return {"loaded": False}
    return {
        "loaded": True,
        "position": p.position,
        "duration": p.duration,
        "playing": p.backend._playing,
        "speed": p.backend._speed,
        "volume": p.backend._volume,
        "filename": p.audio_path.name,
        "metadata": p.metadata,
        "flags": p.flags,
        "harmony_flags": p.harmony_flags,
        "lyrics": p.lyrics,
        "time_signature": p.time_signature,
        "dirty": p._dirty,
        "metronome_enabled": p.backend._metronome_enabled,
        "click_volume": p.backend._click_volume,
        "loop_mode": p.loop_mode,
        "loop_range": p.get_loop_range(),
        "update_counter": p.update_counter,
        "filter_enabled": p.backend._filter_enabled,
        "filter_low_enabled": p.backend._filter_low_enabled,
        "filter_high_enabled": p.backend._filter_high_enabled,
        "filter_low_hz": p.backend._filter_low_hz,
        "filter_high_hz": p.backend._filter_high_hz,
        "can_undo": p._undo.can_undo,
        "can_redo": p._undo.can_redo,
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
