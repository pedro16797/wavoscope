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
import threading
import bisect
from pathlib import Path
from typing import List, Dict, Any, Callable, Tuple

from audio.audio_backend import AudioBackend
from audio.waveform_cache import WaveformCache


class Project:
    # ---------- construction / persistence ----------
    def __init__(self, audio_path: Path) -> None:
        self._callbacks: Dict[str, List[Callable]] = {
            "flag_added": [],
            "flag_removed": [],
        }
        self.audio_path: Path = audio_path
        self.sidecar_path: Path = audio_path.with_suffix(audio_path.suffix + ".oscope")

        self.backend: AudioBackend = AudioBackend()
        self.backend.set_tick_provider(self.subdivision_ticks_between)
        self.backend.set_loop_provider(self.get_loop_range)
        self.loop_mode: str = "none"
        self.session_data: Dict[str, Any] = self._load_or_create_sidecar()

        self.wave_cache: WaveformCache | None = None
        self._dirty: bool = False
        self._lock = threading.RLock()

    # ---------- file handling ----------
    def open_file(self, path: Path) -> None:
        """Close current audio, open new file, build cache."""
        with self._lock:
            print(f"[Project] Opening file: {path}")
            # Stop ongoing playback
            if self.backend._playing:
                self.backend.pause()
            self.backend.close()

            # Load new audio
            try:
                print("[Project] Loading audio into backend...")
                self.backend.open_file(path)
                print(f"[Project] Audio loaded. SR={self.backend._sr}, Duration={self.backend.duration:.2f}s")

                print("[Project] Building waveform cache...")
                self.wave_cache = WaveformCache(self.backend._data, self.backend._sr)
                print("[Project] Waveform cache built")
            except Exception as e:
                print(f"[Project] ERROR loading audio: {e}")
                import traceback
                traceback.print_exc()
                raise

            # Reset caches
            self._spectrum_cache: Dict[str, Any] = {}

    def save(self) -> None:
        """Write current session data to .oscope file."""
        with self._lock:
            try:
                self.sidecar_path.write_text(json.dumps(self.session_data, indent=2))
                self._dirty = False
            except Exception as e:
                print(f"[Project] Error saving sidecar: {e}")

    # ---------- flag API ----------
    @property
    def flags(self) -> List[Dict[str, Any]]:
        """Live, sorted list of rhythm flags (returns a copy for thread safety)."""
        with self._lock:
            return list(self.session_data.setdefault("flags", []))

    @property
    def harmony_flags(self) -> List[Dict[str, Any]]:
        """Live, sorted list of harmony flags (returns a copy for thread safety)."""
        with self._lock:
            return list(self.session_data.setdefault("harmony_flags", []))

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
        with self._lock:
            flags = self.session_data.setdefault("flags", [])
            if any(abs(f["t"] - time) < 0.001 for f in flags):
                return

            flags.append(
                {
                    "t": time,
                    "type": kind,
                    "subdivision": subdivision,
                    "name": name,
                    "is_section_start": section_start,
                    "shaded_subdivisions": shaded,
                }
            )
            flags.sort(key=lambda f: f["t"])
            self._recompute_auto_names()
            self._clear_backend_cache()
            self.mark_dirty()
            self._emit("flag_added", time)

    def remove_flag(self, idx: int) -> None:
        """Delete flag by index."""
        with self._lock:
            flags = self.session_data.setdefault("flags", [])
            if 0 <= idx < len(flags):
                flags.pop(idx)
                self._recompute_auto_names()
                self._clear_backend_cache()
                self.mark_dirty()

    def add_harmony_flag(self, time: float, chord: Dict[str, Any] | None = None) -> None:
        """Insert a new harmony flag."""
        with self._lock:
            flags = self.session_data.setdefault("harmony_flags", [])
            if any(abs(f["t"] - time) < 0.001 for f in flags):
                return

            if chord is None:
                chord = {
                    "root": "C",
                    "accidental": "",
                    "quality": "M",
                    "extension": "",
                    "alterations": [],
                    "additions": [],
                    "bass": "",
                    "bass_accidental": "",
                }

            flags.append({"t": time, "chord": chord})
            flags.sort(key=lambda f: f["t"])
            self.mark_dirty()
            self._emit("flag_added", time)

    def remove_harmony_flag(self, idx: int) -> None:
        """Delete harmony flag by index."""
        with self._lock:
            flags = self.session_data.setdefault("harmony_flags", [])
            if 0 <= idx < len(flags):
                flags.pop(idx)
                self.mark_dirty()
                self._emit("flag_removed", idx)

    def move_harmony_flag(self, idx: int, new_time: float) -> None:
        """Change harmony flag time while enforcing ordering."""
        with self._lock:
            flags = self.session_data.setdefault("harmony_flags", [])
            if 0 <= idx < len(flags):
                flags[idx]["t"] = new_time
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()

    def update_harmony_flag(self, idx: int, time: float, chord: Dict[str, Any]) -> None:
        """Update harmony flag at index."""
        with self._lock:
            flags = self.session_data.setdefault("harmony_flags", [])
            if 0 <= idx < len(flags):
                flags[idx] = {"t": time, "chord": chord}
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()

    def move_flag(self, idx: int, new_time: float) -> None:
        """Change flag time while enforcing ordering."""
        with self._lock:
            flags = self.session_data.setdefault("flags", [])
            if 0 <= idx < len(flags):
                flags[idx]["t"] = new_time
                flags.sort(key=lambda f: f["t"])
                self._recompute_auto_names()
                self._clear_backend_cache()
                self.mark_dirty()

    def update_flag(
        self,
        idx: int,
        time: float,
        kind: str = "rhythm",
        subdivision: int = 0,
        name: str = "",
        section_start: bool = False,
        shaded: bool = False,
    ) -> None:
        """Update all properties of a flag at index."""
        with self._lock:
            flags = self.session_data.setdefault("flags", [])
            if 0 <= idx < len(flags):
                flags[idx] = {
                    "t": time,
                    "type": kind,
                    "subdivision": subdivision,
                    "name": name,
                    "is_section_start": section_start,
                    "shaded_subdivisions": shaded,
                }
                flags.sort(key=lambda f: f["t"])
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

    def set_loop_mode(self, mode: str) -> None:
        """Change looping mode and update backend."""
        with self._lock:
            self.loop_mode = mode
            self.backend.set_loop_enabled(mode != "none")

    # ---------- derived read-only properties ----------
    @property
    def position(self) -> float: return self.backend.position
    @property
    def duration(self) -> float: return self.backend.duration

    def get_loop_range(self, pos: float | None = None) -> Tuple[float, float]:
        """Return (start, end) times for the current loop mode and position."""
        with self._lock:
            if pos is None:
                pos = self.backend.position

            duration = self.duration
            if self.loop_mode == "none":
                return (0.0, duration)

            if self.loop_mode == "whole":
                return (0.0, duration)

            flags = self.flags
            if self.loop_mode == "section":
                section_starts = [f["t"] for f in flags if f.get("is_section_start")]
                if not section_starts:
                    return (0.0, duration)

                idx = bisect.bisect_right(section_starts, pos) - 1
                start = section_starts[idx] if idx >= 0 else 0.0
                end = section_starts[idx + 1] if idx + 1 < len(section_starts) else duration
                return (start, end)

            if self.loop_mode == "bar":
                times = [f["t"] for f in flags if f.get("type") == "rhythm"]
                if not times:
                    return (0.0, duration)

                idx = bisect.bisect_right(times, pos) - 1
                start = times[idx] if idx >= 0 else 0.0
                end = times[idx + 1] if idx + 1 < len(times) else duration
                return (start, end)

            return (0.0, duration)

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
        flags = self.flags

        # Iterate over neighbouring flag pairs
        for i, prev in enumerate(flags):
            if prev["type"] != "rhythm":
                continue

            # Every rhythm flag itself is a strong tick
            if start <= prev["t"] < end:
                ticks.append((prev["t"], True))

            # Subdivisions only exist between this and the next flag
            if i + 1 < len(flags):
                nxt = flags[i + 1]

                # Resolve subdivision (walk backwards if not explicitly set)
                subdiv = prev.get("subdivision", 0)
                if subdiv == 0:
                    for p in reversed(flags[: i + 1]):
                        if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                            subdiv = p["subdivision"]
                            break
                    else:
                        subdiv = 1

                if subdiv > 1:
                    span = nxt["t"] - prev["t"]
                    step = span / subdiv
                    # k=0 is the main flag (already added), so start from 1
                    for k in range(1, subdiv):
                        tick_time = prev["t"] + k * step
                        if start <= tick_time < end:
                            ticks.append((tick_time, False))

        return sorted(ticks, key=lambda t: t[0])

    # ---------- internal utilities ----------
    def _load_or_create_sidecar(self) -> dict[str, Any]:
        if self.sidecar_path.exists():
            try:
                data = json.loads(self.sidecar_path.read_text())
                data.setdefault("harmony_flags", [])
                return data
            except Exception as e:
                print(f"[Project] Error loading sidecar {self.sidecar_path}: {e}")
        return {
            "labels": [],
            "loopPoints": [],
            "lastView": {},
            "flags": [],
            "harmony_flags": [],
        }

    def mark_dirty(self) -> None:
        self._dirty = True

    def _clear_backend_cache(self) -> None:
        self.backend.clear_tick_cache()
        self.backend.reset_loop_range()

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
        with self._lock:
            flags = self.session_data.setdefault("flags", [])
            if not (0 <= left_idx < len(flags) and 0 <= right_idx < len(flags)):
                return

            left = flags[left_idx]
            right = flags[right_idx]
            if right["t"] <= left["t"]:
                return

            span = right["t"] - left["t"]
            step = span / (count + 1)
            subdivision = left.get("subdivision", 0)

            for i in range(1, count + 1):
                t = left["t"] + i * step
                flags.append(
                    {
                        "t": t,
                        "type": "rhythm",
                        "subdivision": subdivision,
                        "name": "",
                        "is_section_start": False,
                        "shaded_subdivisions": False,
                    }
                )

            flags.sort(key=lambda f: f["t"])
            self._recompute_auto_names()
            self._clear_backend_cache()
            self.mark_dirty()
            self._emit("flag_added", left["t"])

    def register_callback(self, event: str, callback: Callable) -> None:
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._callbacks.get(event, []):
            callback(*args, **kwargs)