from fastapi import APIRouter, HTTPException, Response, BackgroundTasks, Depends
from pydantic import BaseModel
from pathlib import Path
import numpy as np
from backend import state
from backend.deps import require_project
from utils.logging import logger
from session.project import Project

router = APIRouter(prefix="/project", tags=["project"])

class FlagData(BaseModel):
    t: float
    type: str = "rhythm"
    div: int = 0
    n: str = ""
    s: bool = False
    divshade: bool = False

class ChordData(BaseModel):
    r: str
    ca: str = ""
    q: str = ""
    ext: str = ""
    alt: list[str] = []
    add: list[str] = []
    b: str = ""
    ba: str = ""

class HarmonyFlagData(BaseModel):
    t: float
    c: ChordData

class TimeSignatureData(BaseModel):
    numerator: int
    denominator: int

@router.post("/flags")
async def add_flag(flag: FlagData, project: Project = Depends(require_project)):
    idx = project.add_flag(
        t=flag.t,
        kind=flag.type,
        div=flag.div,
        n=flag.n,
        s=flag.s,
        divshade=flag.divshade
    )
    return {"status": "ok", "flags": project.flags, "idx": idx}

@router.delete("/flags/{idx}")
async def remove_flag(idx: int, project: Project = Depends(require_project)):
    project.remove_flag(idx)
    return {"status": "ok", "flags": project.flags}

class FlagMove(BaseModel):
    idx: int
    t: float

@router.post("/flags/move")
async def move_flag(move: FlagMove, project: Project = Depends(require_project)):
    res = project.move_flag(move.idx, move.t)
    if res is None:
        raise HTTPException(status_code=404, detail="Flag not found")
    return {"status": "ok", "flags": project.flags, "updated_flag": res["flag"], "new_idx": res["idx"]}

@router.patch("/flags/{idx}")
async def update_flag(idx: int, flag: FlagData, project: Project = Depends(require_project)):
    project.update_flag(
        idx=idx,
        t=flag.t,
        kind=flag.type,
        div=flag.div,
        n=flag.n,
        s=flag.s,
        divshade=flag.divshade
    )
    return {"status": "ok", "flags": project.flags}

class FlagInsertN(BaseModel):
    left_idx: int
    count: int

@router.post("/flags/insert_n")
async def insert_n_flags(data: FlagInsertN, project: Project = Depends(require_project)):
    project.insert_equi_spaced_flags(data.left_idx, data.left_idx + 1, data.count)
    return {"status": "ok", "flags": project.flags}

@router.post("/time_signature")
async def update_time_signature(data: TimeSignatureData, project: Project = Depends(require_project)):
    project.update_time_signature(data.numerator, data.denominator)
    return {"status": "ok", "time_signature": project.time_signature}

@router.post("/harmony_flags")
async def add_harmony_flag(flag: HarmonyFlagData, project: Project = Depends(require_project)):
    idx = project.add_harmony_flag(t=flag.t, chord=flag.c.model_dump())
    return {"status": "ok", "harmony_flags": project.harmony_flags, "idx": idx}

@router.delete("/harmony_flags/{idx}")
async def remove_harmony_flag(idx: int, project: Project = Depends(require_project)):
    project.remove_harmony_flag(idx)
    return {"status": "ok", "harmony_flags": project.harmony_flags}

class HarmonyFlagMove(BaseModel):
    idx: int
    t: float

class LyricData(BaseModel):
    s: str
    t: float
    l: float

class LyricUpdate(BaseModel):
    s: str | None = None
    t: float | None = None
    l: float | None = None

class LyricMove(BaseModel):
    idx: int
    t: float

class LyricSelect(BaseModel):
    idx: int | None = None

@router.post("/lyrics")
async def add_lyric(lyric: LyricData, project: Project = Depends(require_project)):
    res = project.add_lyric(lyric.s, lyric.t, lyric.l)
    return {"status": "ok", "lyrics": project.lyrics, "new_lyric": res["lyric"], "idx": res["idx"]}

@router.delete("/lyrics/{idx}")
async def remove_lyric(idx: int, project: Project = Depends(require_project)):
    project.remove_lyric(idx)
    return {"status": "ok", "lyrics": project.lyrics}

@router.patch("/lyrics/{idx}")
async def update_lyric(idx: int, lyric: LyricUpdate, project: Project = Depends(require_project)):
    res = project.update_lyric(idx, lyric.s, lyric.t, lyric.l)
    if res is None:
        raise HTTPException(status_code=404, detail="Lyric not found")
    return {"status": "ok", "lyrics": project.lyrics, "updated_lyric": res["lyric"], "new_idx": res["idx"]}

@router.post("/lyrics/select")
async def select_lyric(select: LyricSelect, project: Project = Depends(require_project)):
    project.set_selected_lyric(select.idx)
    return {"status": "ok"}

@router.post("/lyrics/move")
async def move_lyric(move: LyricMove, project: Project = Depends(require_project)):
    res = project.move_lyric(move.idx, move.t)
    if res is None:
        raise HTTPException(status_code=404, detail="Lyric not found")
    return {"status": "ok", "lyrics": project.lyrics, "updated_lyric": res["lyric"], "new_idx": res["idx"]}

@router.post("/harmony_flags/move")
async def move_harmony_flag(move: HarmonyFlagMove, project: Project = Depends(require_project)):
    res = project.move_harmony_flag(move.idx, move.t)
    if res is None:
        raise HTTPException(status_code=404, detail="Harmony flag not found")
    return {"status": "ok", "harmony_flags": project.harmony_flags, "updated_flag": res["flag"], "new_idx": res["idx"]}

@router.patch("/harmony_flags/{idx}")
async def update_harmony_flag(idx: int, flag: HarmonyFlagData, project: Project = Depends(require_project)):
    project.update_harmony_flag(idx=idx, t=flag.t, chord=flag.c.model_dump())
    return {"status": "ok", "harmony_flags": project.harmony_flags}

@router.get("/analyze_chord")
async def analyze_chord(t: float, project: Project = Depends(require_project)):
    from audio.chord_analyzer import analyze_chord_at
    from session.chord_utils import default_chord

    # Get audio data from project backend
    y = project.backend._data
    sr = project.backend._sr
    if y is None or sr == 0:
        return default_chord()

    # If stereo, mix to mono for analysis
    y_mono = np.mean(y, axis=1) if len(y.shape) > 1 else y
    return analyze_chord_at(y_mono, sr, t)

@router.post("/save")
async def save_project(project: Project = Depends(require_project)):
    project.save()
    return {"status": "ok"}

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
        logger.exception("bg_export error")
        state.export_message = f"Error: {str(e)}"
    finally:
        import time
        time.sleep(2) # Keep the message for a moment
        state.export_active = False

@router.post("/export/musicxml/start")
async def start_export(data: ExportStartData, background_tasks: BackgroundTasks, project: Project = Depends(require_project)):
    """Starts a background task to export the project to MusicXML."""
    # We copy the data to avoid thread issues if project changes
    session_data = project.session_data.copy()
    audio_name = project.audio_path.name
    audio_duration = project.duration

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
async def export_musicxml(project: Project = Depends(require_project)):
    # Legacy endpoint for browser fallback
    xml_content = project.generate_musicxml()
    filename = project.audio_path.stem + ".musicxml"
    return Response(
        content=xml_content,
        media_type="application/vnd.recordare.musicxml+xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

class OpenProject(BaseModel):
    path: str

@router.get("/undo/steps")
async def get_undo_steps():
    if not state.project:
        return []
    return state.project._undo.get_history()

class UndoRestore(BaseModel):
    index: int

@router.post("/undo/restore")
async def restore_undo(data: UndoRestore, project: Project = Depends(require_project)):
    project.restore_checkpoint(data.index)
    return {
        "status": "ok",
        "flags": project.flags,
        "harmony_flags": project.harmony_flags,
        "lyrics": project.lyrics,
        "time_signature": project.time_signature
    }

@router.post("/undo")
async def undo_project(project: Project = Depends(require_project)):
    project.undo()
    return {
        "status": "ok",
        "flags": project.flags,
        "harmony_flags": project.harmony_flags,
        "lyrics": project.lyrics,
        "time_signature": project.time_signature
    }

@router.post("/open")
async def open_project(data: OpenProject):
    path = Path(data.path)
    if not path.exists():
        logger.error(f"File not found at {data.path}")
        raise HTTPException(status_code=404, detail=f"File not found: {data.path}")

    if state.project:
        state.project.close()

    new_project = Project(path)
    new_project.open_file(path)
    state.project = new_project

    # Register callback for playlist auto-advance
    if state.on_playback_finished:
        state.project.backend.register_callback("finished", state.on_playback_finished)

    return {"status": "ok", "filename": path.name}
