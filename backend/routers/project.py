from fastapi import APIRouter, HTTPException, Response, BackgroundTasks
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

class TimeSignatureData(BaseModel):
    numerator: int
    denominator: int

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
        raise HTTPException(status_code=500, detail=f"Failed to add flag: {str(e)}")

@router.delete("/flags/{idx}")
async def remove_flag(idx: int):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.remove_flag(idx)
        return {"status": "ok", "flags": state.project.flags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove flag: {str(e)}")

class FlagMove(BaseModel):
    idx: int
    t: float

@router.post("/flags/move")
async def move_flag(move: FlagMove):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.move_flag(move.idx, move.t)
        return {"status": "ok", "flags": state.project.flags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move flag: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to update flag: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to insert flags: {str(e)}")

@router.post("/time_signature")
async def update_time_signature(data: TimeSignatureData):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.update_time_signature(data.numerator, data.denominator)
        return {"status": "ok", "time_signature": state.project.time_signature}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update time signature: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to add harmony flag: {str(e)}")

@router.delete("/harmony_flags/{idx}")
async def remove_harmony_flag(idx: int):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.remove_harmony_flag(idx)
        return {"status": "ok", "harmony_flags": state.project.harmony_flags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove harmony flag: {str(e)}")

class HarmonyFlagMove(BaseModel):
    idx: int
    t: float

@router.post("/harmony_flags/move")
async def move_harmony_flag(move: HarmonyFlagMove):
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.move_harmony_flag(move.idx, move.t)
        return {"status": "ok", "harmony_flags": state.project.harmony_flags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move harmony flag: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Failed to update harmony flag: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Chord analysis failed: {str(e)}")

@router.post("/save")
async def save_project():
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        state.project.save()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save project: {str(e)}")

@router.get("/export/musicxml/check")
async def check_export():
    if not state.project:
        return {"can_export": False, "reason": "No project loaded"}
    if not state.project.can_export:
        return {"can_export": False, "reason": "No rhythm flags found. At least one rhythm flag is required to define measures."}
    return {"can_export": True}

class ExportStartData(BaseModel):
    path: str

def bg_export(path: str, session_data: dict, audio_name: str, audio_duration: float):
    state.export_active = True
    state.export_progress = 0.0
    state.export_message = "Starting export..."
    try:
        from session.export import generate_musicxml
        def progress_cb(ratio, msg):
            state.export_progress = ratio
            state.export_message = msg

        xml_content = generate_musicxml(session_data, audio_name, progress_callback=progress_cb, audio_duration=audio_duration)

        state.export_message = "Saving file..."
        Path(path).write_text(xml_content, encoding="utf-8")
        state.export_progress = 1.0
        state.export_message = "Done!"
    except Exception as e:
        print(f"[Backend] bg_export error: {e}")
        traceback.print_exc()
        state.export_message = f"Error: {str(e)}"
    finally:
        import time
        time.sleep(2) # Keep the message for a moment
        state.export_active = False

@router.post("/export/musicxml/start")
async def start_export(data: ExportStartData, background_tasks: BackgroundTasks):
    """Starts a background task to export the project to MusicXML."""
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")

    # We copy the data to avoid thread issues if project changes
    session_data = state.project.session_data.copy()
    audio_name = state.project.audio_path.name
    audio_duration = state.project.duration

    background_tasks.add_task(bg_export, data.path, session_data, audio_name, audio_duration)
    return {"status": "started"}

@router.get("/export/musicxml/progress")
async def get_export_progress():
    return {
        "active": state.export_active,
        "progress": state.export_progress,
        "message": state.export_message
    }

@router.get("/export/musicxml")
async def export_musicxml():
    # Legacy endpoint for browser fallback
    if not state.project:
        raise HTTPException(status_code=400, detail="No project loaded")
    try:
        xml_content = state.project.generate_musicxml()
        filename = state.project.audio_path.stem + ".musicxml"
        return Response(
            content=xml_content,
            media_type="application/vnd.recordare.musicxml+xml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        print(f"[Backend] Error in export_musicxml: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to export MusicXML: {str(e)}")

class OpenProject(BaseModel):
    path: str

@router.post("/open")
async def open_project(data: OpenProject):
    path = Path(data.path)
    if not path.exists():
        print(f"[Backend] Error: File not found at {data.path}")
        raise HTTPException(status_code=404, detail=f"File not found: {data.path}")

    try:
        new_project = Project(path)
        new_project.open_file(path)
        state.project = new_project
        return {"status": "ok", "filename": path.name}
    except Exception as e:
        print(f"[Backend] Exception during open_project: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to open project: {str(e)}")
