from fastapi import APIRouter, HTTPException, Depends
from backend.deps import require_project
from session.project import Project

router = APIRouter(prefix="/audio", tags=["audio"])

@router.get("/waveform")
async def get_waveform(start: float = 0, end: float = 0, n_bars: int = 1000,
                       project: Project = Depends(require_project)):
    if not project.wave_cache:
        raise HTTPException(status_code=400, detail="No audio loaded")

    if end == 0:
        end = project.duration

    bars = project.wave_cache.bars(start, end, n_bars)
    return {"bars": bars}

@router.get("/spectrum")
async def get_spectrum(position: float, window: float = 0.3, low_hz: float = 20,
                       high_hz: float = 20000, width: int = 1000,
                       project: Project = Depends(require_project)):
    if project._data is None:
        raise HTTPException(status_code=400, detail="No audio loaded")

    from audio.spectrum_analyzer import analyze
    f, db = analyze(project._data, project._sr, position, window, low_hz, high_hz, width)
    return {"freqs": f.tolist(), "db": db.tolist()}
