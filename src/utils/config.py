"""
Centralised typed access to persistent settings (JSON + defaults).

Public API
----------
Config().get("ui.theme")        -> str | int | float
Config().set("ui.theme", value) -> None
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CONFIG_PATH = Path.home() / ".wavoscope_config.json"
_DEFAULT_FILE: Path = Path(__file__).resolve().parent.parent.parent / "config" / "default.json"
AUDIO_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg)"


class Config:
    """Singleton thin wrapper around a JSON config file with fall-back to JSON defaults."""

    _instance: Config | None = None

    # ---------- singleton boiler-plate ----------
    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._defaults = {}
            if _DEFAULT_FILE.exists():
                try:
                    cls._instance._defaults = json.loads(_DEFAULT_FILE.read_text(encoding="utf-8"))
                except Exception:
                    pass

            cls._instance._data = {}
            if _CONFIG_PATH.exists():
                try:
                    cls._instance._data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
                except Exception:
                    pass
        return cls._instance

    # ---------- public ----------
    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the stored value for `key`.

        Falls back to default.json, then to `default`.
        """
        if key in self._data:
            return self._data[key]

        # Walk the JSON tree for defaults
        node = self._defaults
        for part in key.split("."):
            if isinstance(node, dict):
                node = node.get(part, {})
            else:
                node = {}
                break

        res = node
        if isinstance(res, dict) and "default" in res:
            res = res["default"]

        return default if res == {} else res

    def get_local_ip(self) -> str:
        """Return the machine's local IP address."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # doesn't even have to be reachable
                s.connect(('10.254.254.254', 1))
                ip = s.getsockname()[0]
            except Exception:
                ip = '127.0.0.1'
            finally:
                s.close()
        except Exception:
            ip = '127.0.0.1'
        return ip

    def set(self, key: str, value: Any) -> None:
        """Store `value` under `key` and flush to disk."""
        self._data[key] = value
        try:
            _CONFIG_PATH.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
