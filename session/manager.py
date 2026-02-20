from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from utils.logging import logger

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
                data.setdefault("harmony_flags", [])
                data.setdefault("time_signature", {"numerator": 4, "denominator": 4})
                data.setdefault("lyrics", [])
                return self._fill_defaults(data)
            except Exception as e:
                logger.error(f"Error loading sidecar {self.sidecar_path}: {e}")
        return self._fill_defaults({
            "labels": [],
            "loopPoints": [],
            "lastView": {},
            "flags": [],
            "harmony_flags": [],
            "lyrics": [],
            "time_signature": {"numerator": 4, "denominator": 4}
        })

    def save(self):
        try:
            scrubbed_data = self._scrub_defaults(self.session_data)
            self.sidecar_path.write_text(json.dumps(scrubbed_data, indent=2, ensure_ascii=False), encoding="utf-8")
            self._dirty = False
        except Exception as e:
            logger.error(f"Error saving sidecar: {e}")

    def _scrub_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        import copy
        data = copy.deepcopy(data)

        if "flags" in data:
            for f in data["flags"]:
                f.pop("auto_name", None)
                if f.get("type") == "rhythm": f.pop("type", None)
                if f.get("div") == 0: f.pop("div", None)
                if f.get("n") == "": f.pop("n", None)
                if f.get("s") is False: f.pop("s", None)
                if f.get("divshade") is False: f.pop("divshade", None)

        if "harmony_flags" in data:
            for f in data["harmony_flags"]:
                chord = f.get("c", {})
                if chord.get("ca") == "": chord.pop("ca", None)
                if chord.get("q") in ["", "M"]: chord.pop("q", None)
                if chord.get("ext") == "": chord.pop("ext", None)
                if chord.get("alt") == []: chord.pop("alt", None)
                if chord.get("add") == []: chord.pop("add", None)
                if chord.get("b") == "": chord.pop("b", None)
                if chord.get("ba") == "": chord.pop("ba", None)

        return data

    def _fill_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "flags" in data:
            for f in data["flags"]:
                f.setdefault("type", "rhythm")
                f.setdefault("div", 0)
                f.setdefault("n", "")
                f.setdefault("s", False)
                f.setdefault("divshade", False)

        if "harmony_flags" in data:
            for f in data["harmony_flags"]:
                chord = f.setdefault("c", {})
                chord.setdefault("r", "C")
                chord.setdefault("ca", "")
                chord.setdefault("q", "")
                chord.setdefault("ext", "")
                chord.setdefault("alt", [])
                chord.setdefault("add", [])
                chord.setdefault("b", "")
                chord.setdefault("ba", "")

        return data

    def mark_dirty(self):
        self._dirty = True
