import json
from pathlib import Path
from PySide6.QtCore import QSettings

_DEFAULT_CFG = Path(__file__).with_suffix('').parent.parent / "config/default.json"
AUDIO_FILTER = "Audio Files (*.wav *.mp3 *.flac *.ogg)"

class Config:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
            cls._inst._settings = QSettings("wavoscope", "wavoscope")
            cls._inst._defaults = json.loads(_DEFAULT_CFG.read_text())
        return cls._inst

    def get(self, key: str, default=None):
        """key is dot-separated, e.g. 'fft.window_s'"""
        val = self._settings.value(key, None)
        if val is not None:
            if isinstance(val, str):
                try:
                    # Try to parse as float
                    if '.' in val:
                        return float(val)
                    return int(val)
                except ValueError:
                    return val
            return val
            
        keys = key.split(".")
        node = self._defaults
        for k in keys:
            node = node.get(k, {})
            if not isinstance(node, dict):
                return node
        return node if node != {} else default

    def set(self, key: str,value):
        """key is dot-separated"""
        self._settings.setValue(key, value)
        self._settings.sync()