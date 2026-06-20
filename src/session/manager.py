from __future__ import annotations
import copy
import json
from pathlib import Path
from typing import Any, Dict
from utils.logging import logger

# Per-item defaults. A field equal to its default is dropped on save (scrub) and
# restored on load (fill), keeping the on-disk *.oscope sidecar compact.
_FLAG_DEFAULTS: Dict[str, Any] = {"type": "rhythm", "div": 0, "n": "", "s": False, "divshade": False}
_CHORD_DEFAULTS: Dict[str, Any] = {"ca": "", "q": "", "ext": "", "alt": [], "add": [], "b": "", "ba": ""}

def _fresh(value: Any) -> Any:
    """Return an independent copy of a default so list defaults aren't shared."""
    return list(value) if isinstance(value, list) else value


class ProjectManager:
    def __init__(self, audio_path: Path):
        self.audio_path = audio_path
        self.sidecar_path = audio_path.with_suffix(audio_path.suffix + ".oscope")
        self.session_data = self._load_or_create_sidecar()
        self._dirty = False

    def _load_or_create_sidecar(self) -> Dict[str, Any]:
        if self.sidecar_path.exists():
            try:
                data = json.loads(self.sidecar_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Error loading sidecar {self.sidecar_path}: {e}")
                data = {}
        else:
            data = {}
        data.setdefault("flags", [])
        data.setdefault("harmony_flags", [])
        data.setdefault("lyrics", [])
        data.setdefault("time_signature", {"numerator": 4, "denominator": 4})
        return self._fill_defaults(data)

    def save(self, path: Path | None = None):
        target = path or self.sidecar_path
        try:
            scrubbed_data = self._scrub_defaults(self.session_data)
            target.write_text(json.dumps(scrubbed_data, indent=2, ensure_ascii=False), encoding="utf-8")
            if path is None:
                self._dirty = False
        except Exception as e:
            logger.error(f"Error saving sidecar to {target}: {e}")

    def _scrub_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = copy.deepcopy(data)

        for f in data.get("flags", []):
            if "t" in f: f["t"] = round(float(f["t"]), 3)
            f.pop("auto_name", None)
            for key, default in _FLAG_DEFAULTS.items():
                if f.get(key) == default: f.pop(key, None)

        for f in data.get("harmony_flags", []):
            if "t" in f: f["t"] = round(float(f["t"]), 3)
            chord = f.get("c", {})
            for key, default in _CHORD_DEFAULTS.items():
                if chord.get(key) == default: chord.pop(key, None)
            # Major quality is the implicit default and is stored as "M" or "".
            if chord.get("q") == "M": chord.pop("q", None)

        for l in data.get("lyrics", []):
            if "t" in l: l["t"] = round(float(l["t"]), 3)
            if "l" in l: l["l"] = round(float(l["l"]), 3)

        return data

    def _fill_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for f in data.get("flags", []):
            for key, default in _FLAG_DEFAULTS.items():
                f.setdefault(key, _fresh(default))

        for f in data.get("harmony_flags", []):
            chord = f.setdefault("c", {})
            chord.setdefault("r", "C")
            for key, default in _CHORD_DEFAULTS.items():
                chord.setdefault(key, _fresh(default))

        return data

    def mark_dirty(self):
        self._dirty = True
