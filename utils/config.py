"""
Centralised typed access to persistent settings (QSettings + defaults).

Public API
----------
Config().get("ui.theme")        -> str | int | float
Config().set("ui.theme", value) -> None
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import QSettings

_DEFAULT_FILE: Path = Path(__file__).with_suffix("") / "../../config/default.json"
AUDIO_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg)"


class Config:
    """Singleton thin wrapper around QSettings with fall-back to JSON defaults."""

    _instance: Config | None = None

    # ---------- singleton boiler-plate ----------
    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = QSettings("wavoscope", "wavoscope")
            cls._instance._defaults = json.loads(_DEFAULT_FILE.read_text())
        return cls._instance

    # ---------- public ----------
    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the stored value for `dotted.key`.

        Falls back to default.json, then to `default`.
        """
        q_value = self._settings.value(key, None)
        if q_value is not None:
            return self._coerce(q_value)

        # Walk the JSON tree
        node = self._defaults
        for part in key.split("."):
            node = node.get(part, {})
            if not isinstance(node, dict):
                return node

        return default if node == {} else node

    def set(self, key: str, value: Any) -> None:
        """Store `value` under `dotted.key` and flush to disk."""
        self._settings.setValue(key, value)
        self._settings.sync()

    # ---------- internals ----------
    @staticmethod
    def _coerce(value: Any) -> Any:
        """Qt gives back strings for everything—try to recover numbers."""
        if isinstance(value, str):
            if value == "true":
                return True
            if value == "false":
                return False
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value  # leave as str
        return value