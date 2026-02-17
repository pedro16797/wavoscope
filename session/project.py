"""
`Project` ties together:
• a backing audio file (via AudioBackend)  
• its companion *.oscope* side-car with flags / labels  
• cached waveform data for drawing
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import List, Dict, Any, Callable, Tuple

from audio.audio_backend import AudioBackend
from audio.waveform_cache import WaveformCache
from session.manager import ProjectManager
from session.flags import FlagManager
from session.looping import LoopingEngine


class Project:
    def __init__(self, audio_path: Path) -> None:
        self._callbacks: Dict[str, List[Callable]] = {
            "flag_added": [],
            "flag_removed": [],
        }
        self.audio_path = audio_path
        self._manager = ProjectManager(audio_path)
        self._flags = FlagManager(self._manager.session_data)
        self._looping = LoopingEngine()

        self.backend = AudioBackend()
        self.backend.set_tick_provider(self.subdivision_ticks_between)

        from utils.config import Config
        cfg = Config()
        self.backend.set_click_volume(cfg.get("ui.click_volume", 0.3))
        self.backend.set_novasr_enabled(cfg.get("ui.high_quality_enhancement", False))
        self.backend.set_loop_provider(self.get_loop_range)

        self.wave_cache: WaveformCache | None = None
        self._lock = threading.RLock()

    # ---------- file handling ----------
    def open_file(self, path: Path) -> None:
        with self._lock:
            if self.backend._playing:
                self.backend.pause()
            try:
                self.backend.open_file(path)
                self.wave_cache = WaveformCache(self.backend._data, self.backend._sr)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise
            self._spectrum_cache: Dict[str, Any] = {}

    def save(self) -> None:
        with self._lock:
            self._manager.save()

    @property
    def sidecar_path(self): return self._manager.sidecar_path
    @property
    def session_data(self): return self._manager.session_data
    @property
    def _dirty(self): return self._manager._dirty
    @_dirty.setter
    def _dirty(self, value): self._manager._dirty = value

    # ---------- flag API ----------
    @property
    def flags(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._flags.flags)

    @property
    def harmony_flags(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._flags.harmony_flags)

    def add_flag(self, time: float, kind: str = "rhythm", subdivision: int = 0, name: str = "", section_start: bool = False, shaded: bool = False) -> None:
        with self._lock:
            if self._flags.add_flag(time, kind, subdivision, name, section_start, shaded):
                self._clear_backend_cache()
                self.mark_dirty()
                self._emit("flag_added", time)

    def remove_flag(self, idx: int) -> None:
        with self._lock:
            if self._flags.remove_flag(idx):
                self._clear_backend_cache()
                self.mark_dirty()

    def add_harmony_flag(self, time: float, chord: Dict[str, Any] | None = None) -> None:
        with self._lock:
            if chord is None:
                chord = {"root": "C", "accidental": "", "quality": "M", "extension": "", "alterations": [], "additions": [], "bass": "", "bass_accidental": ""}
            if self._flags.add_harmony_flag(time, chord):
                self.mark_dirty()
                self._emit("flag_added", time)

    def remove_harmony_flag(self, idx: int) -> None:
        with self._lock:
            if self._flags.remove_harmony_flag(idx):
                self.mark_dirty()
                self._emit("flag_removed", idx)

    def move_harmony_flag(self, idx: int, new_time: float) -> None:
        with self._lock:
            flags = self._flags.harmony_flags
            if 0 <= idx < len(flags):
                flags[idx]["t"] = new_time
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()

    def update_harmony_flag(self, idx: int, time: float, chord: Dict[str, Any]) -> None:
        with self._lock:
            flags = self._flags.harmony_flags
            if 0 <= idx < len(flags):
                flags[idx] = {"t": time, "chord": chord}
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()

    def move_flag(self, idx: int, new_time: float) -> None:
        with self._lock:
            flags = self._flags.flags
            if 0 <= idx < len(flags):
                flags[idx]["t"] = new_time
                flags.sort(key=lambda f: f["t"])
                self._flags._recompute_auto_names()
                self._clear_backend_cache()
                self.mark_dirty()

    def update_flag(self, idx: int, time: float, kind: str = "rhythm", subdivision: int = 0, name: str = "", section_start: bool = False, shaded: bool = False) -> None:
        with self._lock:
            flags = self._flags.flags
            if 0 <= idx < len(flags):
                flags[idx] = {"t": time, "type": kind, "subdivision": subdivision, "name": name, "is_section_start": section_start, "shaded_subdivisions": shaded}
                flags.sort(key=lambda f: f["t"])
                self._flags._recompute_auto_names()
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

    def set_loop_mode(self, mode: str) -> None:
        with self._lock:
            self._looping.set_loop_mode(mode)
            self.backend.set_loop_enabled(mode != "none")
            self.backend.reset_loop_range()

    @property
    def loop_mode(self): return self._looping.loop_mode

    # ---------- derived read-only properties ----------
    @property
    def position(self) -> float: return self.backend.position
    @property
    def duration(self) -> float: return self.backend.duration
    @property
    def _data(self) -> Any: return self.backend._data
    @property
    def _sr(self) -> int: return self.backend._sr

    def get_loop_range(self, pos: float | None = None) -> Tuple[float, float]:
        with self._lock:
            if pos is None:
                # Prioritize active loop from backend if it exists
                if self.backend.active_loop_range:
                    return self.backend.active_loop_range
                pos = self.backend.position
            return self._looping.get_loop_range(pos, self.duration, self._flags.flags)

    # ---------- metronome helpers ----------
    def subdivision_ticks_between(self, start: float, end: float) -> list[tuple[float, bool]]:
        import bisect
        ticks: list[tuple[float, bool]] = []
        flags = self._flags.flags
        for i, prev in enumerate(flags):
            if prev["type"] != "rhythm": continue
            if start <= prev["t"] < end: ticks.append((prev["t"], True))
            if i + 1 < len(flags):
                nxt = flags[i + 1]
                subdiv = prev.get("subdivision", 0)
                if subdiv == 0:
                    for p in reversed(flags[: i + 1]):
                        if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                            subdiv = p["subdivision"]
                            break
                    else: subdiv = 1
                if subdiv > 1:
                    span = nxt["t"] - prev["t"]
                    step = span / subdiv
                    for k in range(1, subdiv):
                        tick_time = prev["t"] + k * step
                        if start <= tick_time < end: ticks.append((tick_time, False))
        return sorted(ticks, key=lambda t: t[0])

    def mark_dirty(self) -> None: self._manager.mark_dirty()
    def _clear_backend_cache(self) -> None:
        self.backend.clear_tick_cache()
        self.backend.reset_loop_range()

    def register_callback(self, event: str, callback: Callable) -> None:
        if event in self._callbacks: self._callbacks[event].append(callback)
    def _emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._callbacks.get(event, []): callback(*args, **kwargs)

    def insert_equi_spaced_flags(self, left_idx: int, right_idx: int, count: int) -> None:
        with self._lock:
            flags = self._flags.flags
            if not (0 <= left_idx < len(flags) and 0 <= right_idx < len(flags)): return
            left, right = flags[left_idx], flags[right_idx]
            if right["t"] <= left["t"]: return
            span = right["t"] - left["t"]
            step = span / (count + 1)
            subdivision = left.get("subdivision", 0)
            for i in range(1, count + 1):
                t = left["t"] + i * step
                flags.append({"t": t, "type": "rhythm", "subdivision": subdivision, "name": "", "is_section_start": False, "shaded_subdivisions": False})
            flags.sort(key=lambda f: f["t"])
            self._flags._recompute_auto_names()
            self._clear_backend_cache()
            self.mark_dirty()
            self._emit("flag_added", left["t"])
