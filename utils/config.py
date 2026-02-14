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

_DEFAULT_FILE: Path = Path(__file__).with_suffix("") / "../../config/default.json"
_CONFIG_FILE: Path = Path.home() / ".wavoscope_config.json"
AUDIO_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg)"


class Config:
    """Singleton thin wrapper around a JSON config file with fall-back to JSON defaults."""

    _instance: Config | None = None

    # ---------- singleton boiler-plate ----------
    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
            cls._instance._defaults = json.loads(_DEFAULT_FILE.read_text())
        return cls._instance

    def _load(self) -> None:
        if _CONFIG_FILE.exists():
            try:
                self._settings = json.loads(_CONFIG_FILE.read_text())
            except Exception:
                self._settings = {}
        else:
            self._settings = {}

    def _save(self) -> None:
        _CONFIG_FILE.write_text(json.dumps(self._settings, indent=2))

    # ---------- public ----------
    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the stored value for `dotted.key`.

        Falls back to default.json, then to `default`.
        """
        # Try to get from user settings
        node = self._settings
        found = True
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                found = False
                break

        if found:
            return node

        # Walk the JSON tree
        node = self._defaults
        for part in key.split("."):
            node = node.get(part, {})
            if not isinstance(node, dict):
                return node

        return default if node == {} else node

    def set(self, key: str, value: Any) -> None:
        """Store `value` under `dotted.key` and flush to disk."""
        parts = key.split(".")
        node = self._settings
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
        self._save()