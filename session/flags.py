from __future__ import annotations
from typing import List, Dict, Any, Callable

class FlagManager:
    def __init__(self, session_data: Dict[str, Any]):
        self.session_data = session_data
        self._recompute_auto_names()

    @property
    def flags(self) -> List[Dict[str, Any]]:
        return self.session_data.setdefault("flags", [])

    @property
    def harmony_flags(self) -> List[Dict[str, Any]]:
        return self.session_data.setdefault("harmony_flags", [])

    def add_flag(self, time: float, kind: str, subdivision: int, name: str, section_start: bool, shaded: bool) -> bool:
        flags = self.flags
        if any(abs(f["t"] - time) < 0.001 for f in flags):
            return False

        flags.append({
            "t": time,
            "type": kind,
            "subdivision": subdivision,
            "name": name,
            "is_section_start": section_start,
            "shaded_subdivisions": shaded,
        })
        flags.sort(key=lambda f: f["t"])
        self._recompute_auto_names()
        return True

    def remove_flag(self, idx: int) -> bool:
        flags = self.flags
        if 0 <= idx < len(flags):
            flags.pop(idx)
            self._recompute_auto_names()
            return True
        return False

    def add_harmony_flag(self, time: float, chord: Dict[str, Any]) -> bool:
        flags = self.harmony_flags
        if any(abs(f["t"] - time) < 0.001 for f in flags):
            return False

        flags.append({"t": time, "chord": chord})
        flags.sort(key=lambda f: f["t"])
        return True

    def remove_harmony_flag(self, idx: int) -> bool:
        flags = self.harmony_flags
        if 0 <= idx < len(flags):
            flags.pop(idx)
            return True
        return False

    def _recompute_auto_names(self) -> None:
        section_idx = 0
        measure = 0

        def get_section_label(idx: int) -> str:
            if idx <= 0: return ""
            res = ""
            while idx > 0:
                idx, rem = divmod(idx - 1, 26)
                res = chr(ord("A") + rem) + res
            return res

        for flag in self.flags:
            if flag["type"] != "rhythm":
                flag["auto_name"] = ""
                continue
            if flag.get("is_section_start", False):
                section_idx += 1
                measure = 0
                flag["auto_name"] = get_section_label(section_idx)
            else:
                measure += 1
                section = get_section_label(section_idx)
                flag["auto_name"] = f"{section}{measure:02d}".lstrip("0") or "00"
