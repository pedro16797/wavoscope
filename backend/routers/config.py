from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend import state

router = APIRouter(prefix="/config", tags=["config"])

class AppConfig(BaseModel):
    theme: Optional[str] = None
    click_volume: Optional[float] = None
    spectrum_keys: Optional[int] = None
    default_output_folder: Optional[str] = None
    musicxml_author: Optional[str] = None
    audio_device: Optional[str] = None
    autosave_enabled: Optional[bool] = None
    autosave_forced: Optional[bool] = None
    autosave_interval: Optional[int] = None
    autosave_max_snapshots: Optional[int] = None
    autosave_path: Optional[str] = None

@router.get("")
async def get_config():
    from utils.config import Config
    cfg = Config()
    return {
        "theme": cfg.get("ui.theme", "dark"),
        "click_volume": cfg.get("ui.click_volume", 0.3),
        "spectrum_keys": cfg.get("ui.spectrum_keys", 37),
        "default_output_folder": cfg.get("ui.default_output_folder", ""),
        "musicxml_author": cfg.get("ui.musicxml_author", ""),
        "audio_device": cfg.get("ui.audio_device", ""),
        "autosave_enabled": cfg.get("autosave.enabled", True),
        "autosave_forced": cfg.get("autosave.forced", False),
        "autosave_interval": cfg.get("autosave.interval_minutes", 5),
        "autosave_max_snapshots": cfg.get("autosave.max_snapshots", 5),
        "autosave_path": cfg.get("autosave.path", "")
    }

@router.post("")
async def update_config(new_cfg: AppConfig):
    from utils.config import Config
    cfg = Config()
    if new_cfg.theme is not None:
        cfg.set("ui.theme", new_cfg.theme)
    if new_cfg.click_volume is not None:
        cfg.set("ui.click_volume", new_cfg.click_volume)
        if state.project:
            state.project.backend.set_click_volume(new_cfg.click_volume)
    if new_cfg.spectrum_keys is not None:
        cfg.set("ui.spectrum_keys", new_cfg.spectrum_keys)
    if new_cfg.default_output_folder is not None:
        cfg.set("ui.default_output_folder", new_cfg.default_output_folder)
    if new_cfg.musicxml_author is not None:
        cfg.set("ui.musicxml_author", new_cfg.musicxml_author)
    if new_cfg.audio_device is not None:
        cfg.set("ui.audio_device", new_cfg.audio_device)
        if state.project:
            state.project.backend.set_device(new_cfg.audio_device if new_cfg.audio_device else None)
    if new_cfg.autosave_enabled is not None:
        cfg.set("autosave.enabled", new_cfg.autosave_enabled)
    if new_cfg.autosave_forced is not None:
        cfg.set("autosave.forced", new_cfg.autosave_forced)
    if new_cfg.autosave_interval is not None:
        cfg.set("autosave.interval_minutes", new_cfg.autosave_interval)
    if new_cfg.autosave_max_snapshots is not None:
        cfg.set("autosave.max_snapshots", new_cfg.autosave_max_snapshots)
    if new_cfg.autosave_path is not None:
        cfg.set("autosave.path", new_cfg.autosave_path)
    return {"status": "ok"}

@router.get("/audio-devices")
async def list_audio_devices():
    from audio.audio_backend import AudioBackend
    return AudioBackend.list_devices()
