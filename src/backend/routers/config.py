from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional
import tempfile
from backend import state
from backend.deps import require_host, is_local_request

router = APIRouter(prefix="/config", tags=["config"])

# Fields that reveal host filesystem layout / identity; blanked for remote
# clients so the documented "remote cannot read host files" guarantee holds.
_HOST_ONLY_CONFIG_FIELDS = ("default_output_folder", "musicxml_author", "autosave_path")

class AppConfig(BaseModel):
    theme: Optional[str] = None
    ui_scale: Optional[float] = None
    click_volume: Optional[float] = None
    spectrum_keys: Optional[int] = None
    default_output_folder: Optional[str] = None
    musicxml_author: Optional[str] = None
    audio_device: Optional[str] = None
    autosave_enabled: Optional[bool] = None
    autosave_forced: Optional[bool] = None
    autosave_interval: Optional[float] = None
    autosave_max_snapshots: Optional[int] = None
    autosave_path: Optional[str] = None
    undo_steps: Optional[int] = None
    language: Optional[str] = None
    remote_access: Optional[bool] = None

@router.get("")
async def get_config(request: Request):
    from utils.config import Config
    cfg = Config()
    data = {
        "theme": cfg.get("ui.theme", "dark"),
        "ui_scale": cfg.get("ui.ui_scale", 1.0),
        "click_volume": cfg.get("ui.click_volume", 0.3),
        "spectrum_keys": cfg.get("ui.spectrum_keys", 37),
        "default_output_folder": cfg.get("ui.default_output_folder", ""),
        "musicxml_author": cfg.get("ui.musicxml_author", ""),
        "audio_device": cfg.get("ui.audio_device", ""),
        "language": cfg.get("ui.language", "en"),
        "autosave_enabled": cfg.get("recovery.autosave_enabled", True),
        "autosave_forced": cfg.get("recovery.autosave_forced", False),
        "autosave_interval": cfg.get("recovery.autosave_interval_minutes", 5),
        "autosave_max_snapshots": cfg.get("recovery.autosave_max_snapshots", 5),
        "autosave_path": cfg.get("recovery.autosave_path", ""),
        "undo_steps": cfg.get("recovery.undo_steps", 50),
        "remote_access": cfg.get("network.remote_access", False)
    }
    if not is_local_request(request):
        for field in _HOST_ONLY_CONFIG_FIELDS:
            data[field] = ""
    return data

@router.post("")
async def update_config(new_cfg: AppConfig, _host: None = Depends(require_host)):
    from utils.config import Config
    cfg = Config()
    if new_cfg.theme is not None:
        cfg.set("ui.theme", new_cfg.theme)
    if new_cfg.ui_scale is not None:
        cfg.set("ui.ui_scale", new_cfg.ui_scale)
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
        cfg.set("recovery.autosave_enabled", new_cfg.autosave_enabled)
    if new_cfg.autosave_forced is not None:
        cfg.set("recovery.autosave_forced", new_cfg.autosave_forced)
    if new_cfg.autosave_interval is not None:
        cfg.set("recovery.autosave_interval_minutes", new_cfg.autosave_interval)
    if new_cfg.autosave_max_snapshots is not None:
        cfg.set("recovery.autosave_max_snapshots", new_cfg.autosave_max_snapshots)
    if new_cfg.autosave_path is not None:
        cfg.set("recovery.autosave_path", new_cfg.autosave_path)
    if new_cfg.undo_steps is not None:
        cfg.set("recovery.undo_steps", new_cfg.undo_steps)
        if state.project:
            state.project._undo.set_max_steps(new_cfg.undo_steps)
    if new_cfg.language is not None:
        cfg.set("ui.language", new_cfg.language)
    if new_cfg.remote_access is not None:
        cfg.set("network.remote_access", new_cfg.remote_access)
    return {"status": "ok"}

@router.get("/audio-devices")
async def list_audio_devices():
    from audio.audio_backend import AudioBackend
    return AudioBackend.list_devices()

@router.get("/temp-dir")
async def get_temp_dir():
    return {"temp_dir": tempfile.gettempdir()}

@router.get("/remote-url")
async def get_remote_url():
    from utils.config import Config
    ip = Config().get_local_ip()
    return {"url": f"http://{ip}:{state.port}"}

@router.get("/bootstrap")
async def bootstrap(request: Request):
    from backend import state
    from backend.routers import locales, themes
    from utils.config import Config
    from audio.audio_backend import AudioBackend
    from backend.main import get_status

    cfg = await get_config(request)
    themes_list = await themes.get_themes()
    locales_list = await locales.list_locales()
    devices = AudioBackend.list_devices()
    status = await get_status()

    return {
        "config": cfg,
        "themes": themes_list,
        "locales": locales_list,
        "audio_devices": devices,
        "status": status
    }
