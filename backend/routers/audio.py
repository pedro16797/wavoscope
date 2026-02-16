from fastapi import APIRouter, HTTPException
from backend import state

router = APIRouter(prefix="/audio", tags=["audio"])

@router.get("/waveform")
async def get_waveform(start: float = 0, end: float = 0, n_bars: int = 1000):
    if not state.project or not state.project.wave_cache:
        raise HTTPException(status_code=400, detail="No project or audio loaded")

    try:
        if end == 0:
            end = state.project.duration

        bars = state.project.wave_cache.bars(start, end, n_bars)
        return {"bars": bars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Waveform generation error: {str(e)}")

@router.get("/spectrum")
async def get_spectrum(position: float, window: float = 0.3, low_hz: float = 20, high_hz: float = 20000, width: int = 1000):
    if not state.project or state.project._data is None:
        raise HTTPException(status_code=400, detail="No audio loaded")

    try:
        from audio.spectrum_analyzer import analyze
        f, db = analyze(state.project._data, state.project._sr, position, window, low_hz, high_hz, width)
        return {"freqs": f.tolist(), "db": db.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spectrum analysis error: {str(e)}")
