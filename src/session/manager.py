from __future__ import annotations
import copy
from pathlib import Path
from typing import Any, Dict
from utils.logging import logger
from utils.persistence import write_json_atomic, read_json, quarantine_corrupt_file

# Bumped when the on-disk *.oscope structure changes; drives migration on load.
SCHEMA_VERSION = 1

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
        data: Dict[str, Any] = {}
        if self.sidecar_path.exists():
            try:
                data = read_json(self.sidecar_path)
                if not isinstance(data, dict):
                    raise ValueError("sidecar root is not a JSON object")
            except Exception as e:
                logger.error(f"Error loading sidecar {self.sidecar_path}: {e}")
                # Preserve the unreadable file instead of silently discarding
                # the user's work by overwriting it on the next save.
                quarantine_corrupt_file(self.sidecar_path)
                data = {}
        return self._migrate(data)

    def _migrate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Bring a loaded session up to the current schema version."""
        version = data.get("version", 0)
        if version > SCHEMA_VERSION:
            logger.warning(
                f"Sidecar {self.sidecar_path} has version {version}, newer than "
                f"supported version {SCHEMA_VERSION}; loading best-effort."
            )
        # No structural migrations are needed yet; future versions add steps here.
        data.setdefault("flags", [])
        data.setdefault("harmony_flags", [])
        data.setdefault("lyrics", [])
        data.setdefault("time_signature", {"numerator": 4, "denominator": 4})
        return self._fill_defaults(data)

    def save(self, path: Path | None = None) -> None:
        """Persist the session to disk atomically.

        Raises on failure so callers (and the user) learn the save did not
        succeed instead of believing their work is safely stored.
        """
        target = path or self.sidecar_path
        scrubbed_data = self._scrub_defaults(self.session_data)
        scrubbed_data["version"] = SCHEMA_VERSION
        write_json_atomic(target, scrubbed_data)
        if path is None:
            self._dirty = False

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
