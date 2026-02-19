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
                data = json.loads(self.sidecar_path.read_text())
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
            self.sidecar_path.write_text(json.dumps(scrubbed_data, indent=2, ensure_ascii=False))
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
                if f.get("subdivision") == 0: f.pop("subdivision", None)
                if f.get("name") == "": f.pop("name", None)
                if f.get("is_section_start") is False: f.pop("is_section_start", None)
                if f.get("shaded_subdivisions") is False: f.pop("shaded_subdivisions", None)

                # Apply renames
                if "subdivision" in f: f["div"] = f.pop("subdivision")
                if "name" in f: f["n"] = f.pop("name")
                if "is_section_start" in f: f["s"] = f.pop("is_section_start")
                if "shaded_subdivisions" in f: f["divshade"] = f.pop("shaded_subdivisions")

        if "harmony_flags" in data:
            for f in data["harmony_flags"]:
                chord = f.get("chord", {})
                if chord.get("accidental") == "": chord.pop("accidental", None)
                if chord.get("quality") in ["", "M"]: chord.pop("quality", None)
                if chord.get("extension") == "": chord.pop("extension", None)
                if chord.get("alterations") == []: chord.pop("alterations", None)
                if chord.get("additions") == []: chord.pop("additions", None)
                if chord.get("bass") == "": chord.pop("bass", None)
                if chord.get("bass_accidental") == "": chord.pop("bass_accidental", None)

                # Apply renames
                if "root" in chord: chord["r"] = chord.pop("root")
                if "accidental" in chord: chord["ca"] = chord.pop("accidental")
                if "quality" in chord: chord["q"] = chord.pop("quality")
                if "extension" in chord: chord["ext"] = chord.pop("extension")
                if "alterations" in chord: chord["alt"] = chord.pop("alterations")
                if "additions" in chord: chord["add"] = chord.pop("additions")
                if "bass" in chord: chord["b"] = chord.pop("bass")
                if "bass_accidental" in chord: chord["ba"] = chord.pop("bass_accidental")

                if "chord" in f: f["c"] = f.pop("chord")

        return data

    def _fill_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "flags" in data:
            for f in data["flags"]:
                # Reverse renames
                if "div" in f: f["subdivision"] = f.pop("div")
                if "n" in f: f["name"] = f.pop("n")
                if "s" in f: f["is_section_start"] = f.pop("s")
                if "divshade" in f: f["shaded_subdivisions"] = f.pop("divshade")

                f.setdefault("type", "rhythm")
                f.setdefault("subdivision", 0)
                f.setdefault("name", "")
                f.setdefault("is_section_start", False)
                f.setdefault("shaded_subdivisions", False)

        if "harmony_flags" in data:
            for f in data["harmony_flags"]:
                # Reverse renames
                if "c" in f: f["chord"] = f.pop("c")
                chord = f.setdefault("chord", {})

                if "r" in chord: chord["root"] = chord.pop("r")
                if "ca" in chord: chord["accidental"] = chord.pop("ca")
                if "q" in chord: chord["quality"] = chord.pop("q")
                if "ext" in chord: chord["extension"] = chord.pop("ext")
                if "alt" in chord: chord["alterations"] = chord.pop("alt")
                if "add" in chord: chord["additions"] = chord.pop("add")
                if "b" in chord: chord["bass"] = chord.pop("b")
                if "ba" in chord: chord["bass_accidental"] = chord.pop("ba")

                chord.setdefault("root", "C")
                chord.setdefault("accidental", "")
                chord.setdefault("quality", "")
                chord.setdefault("extension", "")
                chord.setdefault("alterations", [])
                chord.setdefault("additions", [])
                chord.setdefault("bass", "")
                chord.setdefault("bass_accidental", "")

        return data

    def mark_dirty(self):
        self._dirty = True
