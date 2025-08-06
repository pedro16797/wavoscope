from pathlib import Path
from PySide6.QtGui import QColor
import json

PALETTE = {
    "accent": "#0af",
    "background": "#121212",
    "grid": "#444",
    "text": "#e0e0e0",
    "keyWhite": "#ddd",
    "keyBlack": "#888"
}

THEMES_DIR = Path(__file__).parent / "themes"

def full_stylesheet(name):
    palette = load_palette(name)
    qss = load_theme(name)
    for k, v in palette.items():
        qss = qss.replace("{" + k + "}", v)
    return qss

def load_palette(theme="dark"):
    path = THEMES_DIR / f"{theme}.json"
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return PALETTE

def load_theme(name: str) -> str:
    qss_path = THEMES_DIR / f"{name}.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""

def get_waveform_color(theme="dark"):
    palette = load_palette(theme)
    return QColor(palette.get("waveform", palette["accent"]))

def get_spectrum_color(theme="dark"):
    palette = load_palette(theme)
    return QColor(palette.get("spectrum", palette["accent"]))