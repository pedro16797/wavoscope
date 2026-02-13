"""
`Project` ties together:

• a backing audio file (via AudioBackend)  
• its companion *.oscope* side-car with flags / labels  
• cached waveform data for drawing

Public workflow
---------------
project = Project(audio_path)
project.open_file(audio_path)   # loads audio
project.add_flag(t, "rhythm")   # etc.
project.save()                  # writes .oscope
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Callable

from wavoscope.audio.audio_backend import AudioBackend
from wavoscope.audio.waveform_cache import WaveformCache


class Project:
    # ---------- construction / persistence ----------
    def __init__(self, audio_path: Path) -> None:
        self._flag_added_callbacks: List[Callable[[float], None]] = []
        self._flag_removed_callbacks: List[Callable[[int], None]] = []
        self.audio_path: Path = audio_path
        self.sidecar_path: Path = audio_path.with_suffix(audio_path.suffix + "oscope")

        self.backend: AudioBackend = AudioBackend()
        self.session_data: Dict[str, Any] = self._load_or_create_sidecar()

        self.wave_cache: WaveformCache | None = None
        self._dirty: bool = False

    # ---------- file handling ----------
    def open_file(self, path: Path) -> None:
        """Close current audio, open new file, build cache."""
        # Stop ongoing playback
        if self.backend._playing:
            self.backend.pause()
        self.backend.close()

        # Load new audio
        self.backend.open_file(path)
        self.wave_cache = WaveformCache(self.backend._data, self.backend._sr)

        # Reset caches
        self._spectrum_cache: Dict[str, Any] = {}

    def save(self) -> None:
        """Write current session data to .oscope file."""
        self.sidecar_path.write_text(json.dumps(self.session_data, indent=2))
        self._dirty = False

    # ---------- flag API ----------
    @property
    def flags(self) -> List[Dict[str, Any]]:
        """Live, sorted list of flags (in-place edits are allowed)."""
        return self.session_data.setdefault("flags", [])

    def on_flag_added(self, callback: Callable[[float], None]) -> None:
        self._flag_added_callbacks.append(callback)

    def on_flag_removed(self, callback: Callable[[int], None]) -> None:
        self._flag_removed_callbacks.append(callback)

    def add_flag(
        self,
        time: float,
        kind: str = "rhythm",
        subdivision: int = 0,
        name: str = "",
        section_start: bool = False,
        shaded: bool = False,
    ) -> None:
        """Insert and sort a new flag, skipping duplicates < 1 ms."""
        if any(abs(f["t"] - time) < 0.001 for f in self.flags):
            return

        self.flags.append(
            {
                "t": time,
                "type": kind,
                "subdivision": subdivision,
                "name": name,
                "is_section_start": section_start,
                "shaded_subdivisions": shaded,
            }
        )
        self.flags.sort(key=lambda f: f["t"])
        self._recompute_auto_names()
        self._clear_backend_cache()
        self.mark_dirty()
        for cb in self._flag_added_callbacks:
            cb(time)

    def remove_flag(self, idx: int) -> None:
        """Delete flag by index."""
        self.flags.pop(idx)
        self._recompute_auto_names()
        self._clear_backend_cache()
        self.mark_dirty()
        for cb in self._flag_removed_callbacks:
            cb(idx)

    def move_flag(self, idx: int, new_time: float) -> None:
        """Change flag time while enforcing ordering."""
        if 0 <= idx < len(self.flags):
            self.flags[idx]["t"] = new_time
            self.flags.sort(key=lambda f: f["t"])
            self._recompute_auto_names()
            self._clear_backend_cache()
            self.mark_dirty()

    # ---------- playback passthrough ----------
    def seek(self, time: float) -> None: self.backend.seek(time)
    def pause(self) -> None: self.backend.pause()
    def play(self) -> None:
        if not self.backend._playing:
            self._last_play_start = self.backend.position
        self.backend.play()

    def set_speed(self, speed: float) -> None: self.backend.set_speed(speed)
    def set_volume(self, volume: float) -> None: self.backend.set_volume(volume)

    # ---------- derived read-only properties ----------
    @property
    def position(self) -> float: return self.backend.position
    @property
    def duration(self) -> float: return self.backend.duration
    @property
    def _data(self) -> Any: return self.backend._data
    @property
    def _sr(self) -> int: return self.backend._sr

    # ---------- metronome helpers ----------
    def subdivision_ticks_between(self, start: float, end: float) -> list[tuple[float, bool]]:
        """
        Return (time, is_strong) ticks between two play-head positions,
        honouring subdivision flags.
        """
        ticks: list[tuple[float, bool]] = []

        # Iterate over neighbouring flag pairs
        for prev, nxt in zip(self.flags, self.flags[1:]):
            if prev["type"] != "rhythm":
                continue

            # Resolve subdivision (walk backwards if not explicitly set)
            subdiv = prev.get("subdivision", 0)
            if subdiv == 0:
                for p in reversed(self.flags[: self.flags.index(prev) + 1]):
                    if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                        subdiv = p["subdivision"]
                        break
                else:
                    subdiv = 1

            if subdiv <= 1:
                if start <= prev["t"] < end:
                    ticks.append((prev["t"], True))
                continue

            # Evenly spaced ticks within the span
            span = nxt["t"] - prev["t"]
            step = span / subdiv
            for k in range(subdiv):
                tick_time = prev["t"] + k * step
                if start <= tick_time < end:
                    ticks.append((tick_time, k == 0))  # first tick is strong

        return sorted(ticks, key=lambda t: t[0])

    # ---------- internal utilities ----------
    def _load_or_create_sidecar(self) -> dict[str, Any]:
        if self.sidecar_path.exists():
            return json.loads(self.sidecar_path.read_text())
        return {"labels": [], "loopPoints": [], "lastView": {}}

    def mark_dirty(self) -> None:
        self._dirty = True

    def _clear_backend_cache(self) -> None:
        self.backend.clear_tick_cache()

    def _recompute_auto_names(self) -> None:
        """Auto-generate A, A-01, A-02… names for rhythm flags."""
        section_idx = 0
        measure = 0

        for flag in self.flags:
            if flag["type"] != "rhythm":
                flag["auto_name"] = ""
                continue

            if flag.get("is_section_start", False):
                section_idx += 1
                measure = 0
                flag["auto_name"] = chr(ord("A") + section_idx - 1)
            else:
                measure += 1
                section = chr(ord("A") + section_idx - 1) if section_idx else ""
                flag["auto_name"] = f"{section}{measure:02d}".lstrip("0") or "00"

    # ---------- bulk helpers ----------
    def insert_equi_spaced_flags(
        self, left_idx: int, right_idx: int, count: int
    ) -> None:
        """
        Insert `count` evenly-spaced rhythm flags between two existing flags.
        """
        if not (0 <= left_idx < len(self.flags) and 0 <= right_idx < len(self.flags)):
            return

        left = self.flags[left_idx]
        right = self.flags[right_idx]
        if right["t"] <= left["t"]:
            return

        span = right["t"] - left["t"]
        step = span / (count + 1)
        subdivision = left.get("subdivision", 0)

        for i in range(1, count + 1):
            t = left["t"] + i * step
            self.flags.append(
                {
                    "t": t,
                    "type": "rhythm",
                    "subdivision": subdivision,
                    "name": "",
                    "is_section_start": False,
                    "shaded_subdivisions": False,
                }
            )

        self.flags.sort(key=lambda f: f["t"])
        self._recompute_auto_names()
        self._clear_backend_cache()
        self.mark_dirty()
        for cb in self._flag_added_callbacks:
            cb(left["t"])