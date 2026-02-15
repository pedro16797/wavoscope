from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import traceback
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
