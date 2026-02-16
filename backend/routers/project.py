from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import traceback
import numpy as np
from backend import state
from session.project import Project

router = APIRouter(prefix="/project", tags=["project"])

class FlagData(BaseModel):
    t: float
    type: str = "rhythm"
    subdivision: int = 0
    name: str = ""
    is_section_start: bool = False
    shaded_subdivisions: bool = False

class ChordData(BaseModel):
    root: str
    accidental: str = ""
    quality: str = "M"
    extension: str = ""
    alterations: list[str] = []
    additions: list[str] = []
    bass: str = ""
    bass_accidental: str = ""

class HarmonyFlagData(BaseModel):
    t: float
    chord: ChordData

@router.post("/flags")
async def add_flag(flag: FlagData):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.add_flag(
            flag.t,
            flag.type,
            flag.subdivision,
            flag.name,
            flag.is_section_start,
            flag.shaded_subdivisions
        )
        return {"status": "ok", "flags": state.project.flags}
    except Exception as e:
        print(f"[Backend] Error in add_flag: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/flags/{idx}")
async def remove_flag(idx: int):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    state.project.remove_flag(idx)
    return {"status": "ok", "flags": state.project.flags}

class FlagMove(BaseModel):
    idx: int
    t: float

@router.post("/flags/move")
async def move_flag(move: FlagMove):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    state.project.move_flag(move.idx, move.t)
    return {"status": "ok", "flags": state.project.flags}

@router.patch("/flags/{idx}")
async def update_flag(idx: int, flag: FlagData):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.update_flag(
            idx,
            flag.t,
            flag.type,
            flag.subdivision,
            flag.name,
            flag.is_section_start,
            flag.shaded_subdivisions
        )
        return {"status": "ok", "flags": state.project.flags}
    except Exception as e:
        print(f"[Backend] Error in update_flag: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class FlagInsertN(BaseModel):
    left_idx: int
    count: int

@router.post("/flags/insert_n")
async def insert_n_flags(data: FlagInsertN):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.insert_equi_spaced_flags(data.left_idx, data.left_idx + 1, data.count)
        return {"status": "ok", "flags": state.project.flags}
    except Exception as e:
        print(f"[Backend] Error in insert_n_flags: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/harmony_flags")
async def add_harmony_flag(flag: HarmonyFlagData):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.add_harmony_flag(flag.t, flag.chord.model_dump())
        return {"status": "ok", "harmony_flags": state.project.harmony_flags}
    except Exception as e:
        print(f"[Backend] Error in add_harmony_flag: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/harmony_flags/{idx}")
async def remove_harmony_flag(idx: int):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    state.project.remove_harmony_flag(idx)
    return {"status": "ok", "harmony_flags": state.project.harmony_flags}

class HarmonyFlagMove(BaseModel):
    idx: int
    t: float

@router.post("/harmony_flags/move")
async def move_harmony_flag(move: HarmonyFlagMove):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    state.project.move_harmony_flag(move.idx, move.t)
    return {"status": "ok", "harmony_flags": state.project.harmony_flags}

@router.patch("/harmony_flags/{idx}")
async def update_harmony_flag(idx: int, flag: HarmonyFlagData):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.update_harmony_flag(idx, flag.t, flag.chord.model_dump())
        return {"status": "ok", "harmony_flags": state.project.harmony_flags}
    except Exception as e:
        print(f"[Backend] Error in update_harmony_flag: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze_chord")
async def analyze_chord(t: float):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    from audio.chord_analyzer import analyze_chord_at
    try:
        # Get audio data from project backend
        y = state.project.backend._data
        sr = state.project.backend._sr
        if y is None or sr == 0:
             return {
                "root": "C",
                "accidental": "",
                "quality": "M",
                "extension": "",
                "alterations": [],
                "additions": [],
                "bass": "",
                "bass_accidental": "",
            }

        # If stereo, mix to mono for analysis
        if len(y.shape) > 1:
            y_mono = np.mean(y, axis=1)
        else:
            y_mono = y

        suggestion = analyze_chord_at(y_mono, sr, t)
        return suggestion
    except Exception as e:
        print(f"[Backend] Error in analyze_chord: {e}")
        traceback.print_exc()
        return {
            "root": "C",
            "accidental": "",
            "quality": "M",
            "extension": "",
            "alterations": [],
            "additions": [],
            "bass": "",
            "bass_accidental": "",
        }

@router.post("/save")
async def save_project():
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    state.project.save()
    return {"status": "ok"}

class OpenProject(BaseModel):
    path: str

@router.post("/open")
async def open_project(data: OpenProject):
    print(f"[Backend] open_project called for: {data.path}")
    path = Path(data.path)
    if not path.exists():
        print(f"[Backend] Error: File not found at {data.path}")
        raise HTTPException(status_code=404, detail=f"File not found: {data.path}")

    try:
        print("[Backend] Initializing new Project object...")
        new_project = Project(path)
        print("[Backend] Calling open_file on project...")
        new_project.open_file(path)
        state.project = new_project
        print("[Backend] Project loaded successfully")
        return {"status": "ok", "filename": path.name}
    except Exception as e:
        print(f"[Backend] Exception during open_project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
