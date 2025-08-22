"""
Centralised colour / stylesheet loader for all GUI widgets.

Reads JSON palettes (with optional “inherits”) and merges them into QSS.
"""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtGui import QColor

AVAILABLE_THEMES = ["oled", "dark", "cosmic", "neon", "light", "warm", "toy", "doll"]
_PALETTE = {
    "accent": "#0af",
    "background": "#121212",
    "grid": "#444",
    "text": "#e0e0e0",
    "keyWhite": "#ddd",
    "keyBlack": "#888",
}
_THEMES_DIR = Path(__file__).with_suffix("").parent / "themes"


def current_theme() -> str:
    """Return the user-selected theme name (cached)."""
    # Late import to avoid circular dependency
    from wavoscope.utils.config import Config

    return Config().get("ui.theme", "dark")


def load_palette(name: str = "dark") -> dict[str, str]:
    """Load and merge palette JSON (supports inheritance)."""
    path = _THEMES_DIR / f"{name}.json"
    try:
        palette = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return _PALETTE

    if "inherits" in palette:
        parent = load_palette(palette["inherits"])
        parent.update(palette)
        return parent

    return palette


def load_theme(name: str) -> str:
    """Read raw QSS template for the requested theme."""
    name = name if name in AVAILABLE_THEMES else "dark"
    qss_path = _THEMES_DIR / f"{name}.qss"
    return qss_path.read_text(encoding="utf-8") if qss_path.exists() else ""


def full_stylesheet(name: str) -> str:
    """Merge palette into QSS template."""
    palette = load_palette(name)
    qss = load_theme(name)
    for key, value in palette.items():
        qss = qss.replace("{" + key + "}", value)
    return qss


# Convenience accessors for single colours
def get_waveform_color(theme: str = "dark") -> QColor:
    palette = load_palette(theme)
    return QColor(palette.get("waveform", palette["accent"]))


def get_spectrum_color(theme: str = "dark") -> QColor:
    palette = load_palette(theme)
    return QColor(palette.get("spectrum", palette["accent"]))