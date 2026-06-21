from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from typing import Optional
from backend.deps import require_project
from session.project import Project

router = APIRouter(prefix="/audio", tags=["audio"])

@router.get("/waveform")
async def get_waveform(start: float = 0, end: Optional[float] = None, n_bars: int = 1000,
                       project: Project = Depends(require_project)):
    if not project.wave_cache:
        raise HTTPException(status_code=400, detail="No audio loaded")

    if end is None:
        end = project.duration

    # Bucketing scans the whole slice; keep it off the event loop.
    bars = await run_in_threadpool(project.wave_cache.bars, start, end, n_bars)
    return {"bars": bars}

@router.get("/spectrum")
async def get_spectrum(position: float, window: float = 0.3, low_hz: float = 20,
                       high_hz: float = 20000, width: int = 1000,
                       project: Project = Depends(require_project)):
    if project._data is None:
        raise HTTPException(status_code=400, detail="No audio loaded")

    from audio.spectrum_analyzer import analyze
    # The FFT is CPU-heavy and fetched on every position tick; run it in a
    # threadpool so it doesn't block the WebSocket broadcast loop.
    f, db = await run_in_threadpool(
        analyze, project._data, project._sr, position, window, low_hz, high_hz, width
    )
    return {"freqs": f.tolist(), "db": db.tolist()}

