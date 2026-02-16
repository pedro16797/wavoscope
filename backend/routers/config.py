from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend import state

router = APIRouter(prefix="/config", tags=["config"])

class AppConfig(BaseModel):
    theme: Optional[str] = None
    click_volume: Optional[float] = None
    spectrum_keys: Optional[int] = None
    high_quality_enhancement: Optional[bool] = None

@router.get("")
async def get_config():
    from utils.config import Config
    cfg = Config()
    return {
        "theme": cfg.get("ui.theme", "dark"),
        "click_volume": cfg.get("ui.click_volume", 0.3),
        "spectrum_keys": cfg.get("ui.spectrum_keys", 37),
        "high_quality_enhancement": cfg.get("ui.high_quality_enhancement", False)
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
            state.project.backend.set_click_gain(new_cfg.click_volume)
    if new_cfg.spectrum_keys is not None:
        cfg.set("ui.spectrum_keys", new_cfg.spectrum_keys)
    if new_cfg.high_quality_enhancement is not None:
        cfg.set("ui.high_quality_enhancement", new_cfg.high_quality_enhancement)
        if state.project:
            state.project.backend.set_novasr_enabled(new_cfg.high_quality_enhancement)
    return {"status": "ok"}
