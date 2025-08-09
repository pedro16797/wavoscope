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

AVAILABLE_THEMES = ["dark", "light", "neon", "warm", "cosmic"]
THEMES_DIR = Path(__file__).parent / "themes"

def full_stylesheet(name):
    palette = load_palette(name)
    qss = load_theme(name)
    for k, v in palette.items():
        qss = qss.replace("{" + k + "}", v)
    return qss

def load_palette(theme="dark"):
    try:
        path = THEMES_DIR / f"{theme}.json"
        palette = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return PALETTE

    # Merge parent if "inherits" key is present
    if "inherits" in palette:
        parent = load_palette(palette["inherits"])
        parent.update(palette)
        return parent

    return palette

def load_theme(name: str) -> str:
    if name not in AVAILABLE_THEMES:
        name = "dark"
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