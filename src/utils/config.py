"""
Centralised typed access to persistent settings (JSON + defaults).

Public API
----------
Config().get("ui.theme")        -> str | int | float
Config().set("ui.theme", value) -> None
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from utils.logging import logger
from utils.persistence import write_json_atomic, read_json

_CONFIG_PATH = Path.home() / ".wavoscope_config.json"
_DEFAULT_FILE: Path = Path(__file__).resolve().parent.parent.parent / "config" / "default.json"
AUDIO_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg)"


class Config:
    """Singleton thin wrapper around a JSON config file with fall-back to JSON defaults."""

    _instance: Config | None = None
    _init_lock = threading.Lock()

    # ---------- singleton boiler-plate ----------
    def __new__(cls) -> Config:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._lock = threading.RLock()
                    inst._defaults = {}
                    if _DEFAULT_FILE.exists():
                        try:
                            inst._defaults = read_json(_DEFAULT_FILE)
                        except Exception:
                            pass

                    inst._data = {}
                    if _CONFIG_PATH.exists():
                        try:
                            inst._data = read_json(_CONFIG_PATH)
                        except Exception:
                            pass
                    cls._instance = inst
        return cls._instance

    # ---------- public ----------
    def get(self, key: str, default: Any = None) -> Any:
        """
        Return the stored value for `key`.

        Falls back to default.json, then to `default`.
        """
        with self._lock:
            if key in self._data:
                return self._data[key]

        # `_defaults` is built once at init and never mutated, so it needs no lock.
        node: Any = self._defaults
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default

        # A wrapper node carries its value under "default"; a plain dict subtree
        # (e.g. ui.keybinds) is returned as-is.
        if isinstance(node, dict):
            return node["default"] if "default" in node else node
        return node

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
        """Store `value` under `key` and flush to disk atomically."""
        # Hold the lock across the write so concurrent set() calls can't have
        # their disk writes reordered (which could persist a stale snapshot).
        # Config writes are infrequent, so serializing them is fine.
        with self._lock:
            self._data[key] = value
            try:
                write_json_atomic(_CONFIG_PATH, dict(self._data))
            except Exception as e:
                logger.error(f"Failed to persist config to {_CONFIG_PATH}: {e}")
