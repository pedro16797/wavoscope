from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

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
                return data
            except Exception as e:
                print(f"[ProjectManager] Error loading sidecar {self.sidecar_path}: {e}")
        return {
            "labels": [],
            "loopPoints": [],
            "lastView": {},
            "flags": [],
            "harmony_flags": [],
        }

    def save(self):
        try:
            self.sidecar_path.write_text(json.dumps(self.session_data, indent=2))
            self._dirty = False
        except Exception as e:
            print(f"[ProjectManager] Error saving sidecar: {e}")

    def mark_dirty(self):
        self._dirty = True
