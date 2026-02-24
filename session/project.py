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
from utils.logging import logger
from session.manager import ProjectManager
from session.flags import FlagManager
from session.looping import LoopingEngine
from session.undo import UndoManager


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
        self.selected_lyric_idx: int | None = None

        from utils.config import Config
        cfg = Config()
        self._undo = UndoManager(self.session_data, max_steps=cfg.get("recovery.undo_steps", 50))

        self.backend = AudioBackend()
        self.backend.set_tick_provider(self.subdivision_ticks_between)

        self.metadata: Dict[str, str] = {"title": "", "artist": "", "album": ""}

        from utils.config import Config
        cfg = Config()
        device_name = cfg.get("ui.audio_device", "")
        if device_name:
            self.backend.set_device(device_name)

        self.backend.set_click_volume(cfg.get("ui.click_volume", 0.3))
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
                self._extract_metadata(path)
            except Exception as e:
                logger.exception("Failed to open audio file")
                raise

    def close(self) -> None:
        with self._lock:
            self.backend.close()

    def _extract_metadata(self, path: Path) -> None:
        try:
            from tinytag import TinyTag
            tag = TinyTag.get(str(path))
            self.metadata = {
                "title": tag.title or "",
                "artist": tag.artist or "",
                "album": tag.album or ""
            }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            self.metadata = {"title": "", "artist": "", "album": ""}

    def save(self) -> None:
        with self._lock:
            self._manager.save()

    @property
    def sidecar_path(self): return self._manager.sidecar_path
    @property
    def session_data(self): return self._manager.session_data

    @property
    def time_signature(self) -> Dict[str, int]:
        return self.session_data.get("time_signature", {"numerator": 4, "denominator": 4})

    @property
    def can_export(self) -> bool:
        with self._lock:
            return any(f.get("type", "rhythm") == "rhythm" for f in self._flags.flags)

    def update_time_signature(self, numerator: int, denominator: int) -> None:
        with self._lock:
            self.session_data["time_signature"] = {"numerator": numerator, "denominator": denominator}
            self.mark_dirty()
            self.checkpoint(f"Time Signature: {numerator}/{denominator}")

    def generate_musicxml(self) -> str:
        from session.export import generate_musicxml
        return generate_musicxml(self.session_data, self.audio_path.name, audio_duration=self.duration)

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

    @property
    def lyrics(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.session_data.get("lyrics", []))

    def add_flag(self, t: float, kind: str = "rhythm", div: int = 0, n: str = "", s: bool = False, divshade: bool = False) -> int:
        with self._lock:
            idx = self._flags.add_flag(t, kind, div, n, s, divshade)
            if idx != -1:
                self._clear_backend_cache()
                self.mark_dirty()
                self._emit("flag_added", t)
                self.checkpoint(f"Added Rhythm Flag at {t:.3f}s")
            return idx

    def remove_flag(self, idx: int) -> None:
        with self._lock:
            if self._flags.remove_flag(idx):
                self._clear_backend_cache()
                self.mark_dirty()
                self._emit("flag_removed", idx)
                self.checkpoint("Removed Rhythm Flag")

    def add_harmony_flag(self, t: float, chord: Dict[str, Any] | None = None) -> int:
        with self._lock:
            if chord is None:
                chord = {"r": "C", "ca": "", "q": "", "ext": "", "alt": [], "add": [], "b": "", "ba": ""}
            idx = self._flags.add_harmony_flag(t, chord)
            if idx != -1:
                self.mark_dirty()
                self._emit("flag_added", t)
                self.checkpoint(f"Added Chord Flag at {t:.3f}s")
            return idx

    def remove_harmony_flag(self, idx: int) -> None:
        with self._lock:
            if self._flags.remove_harmony_flag(idx):
                self.mark_dirty()
                self._emit("flag_removed", idx)
                self.checkpoint("Removed Chord Flag")

    def add_lyric(self, s: str, t: float, l: float) -> dict:
        with self._lock:
            lyrics = self.session_data.get("lyrics", [])
            new_lyric = {"s": s, "t": t, "l": l}
            lyrics.append(new_lyric)
            lyrics.sort(key=lambda item: item["t"])
            self.session_data["lyrics"] = lyrics
            self.mark_dirty()
            self.checkpoint(f"Added Lyric: {s}")
            idx = lyrics.index(new_lyric)
            return {"idx": idx, "lyric": new_lyric}

    def remove_lyric(self, idx: int) -> None:
        with self._lock:
            lyrics = self.session_data.get("lyrics", [])
            if 0 <= idx < len(lyrics):
                lyrics.pop(idx)
                self.mark_dirty()
                self.checkpoint("Removed Lyric")

    def update_lyric(self, idx: int, s: str | None = None, t: float | None = None, l: float | None = None) -> dict | None:
        with self._lock:
            lyrics = self.session_data.get("lyrics", [])
            if 0 <= idx < len(lyrics):
                lyric = lyrics[idx]
                if s is not None: lyric["s"] = s
                if t is not None: lyric["t"] = t
                if l is not None: lyric["l"] = l
                lyrics.sort(key=lambda item: item["t"])
                self.mark_dirty()
                self.checkpoint(f"Updated Lyric: {lyric['s']}")
                self.backend.reset_loop_range()
                new_idx = lyrics.index(lyric)
                return {"idx": new_idx, "lyric": lyric}
            return None

    def set_selected_lyric(self, idx: int | None) -> None:
        with self._lock:
            self.selected_lyric_idx = idx
            self.backend.reset_loop_range()

    def move_lyric(self, idx: int, t: float) -> dict | None:
        with self._lock:
            lyrics = self.session_data.get("lyrics", [])
            if 0 <= idx < len(lyrics):
                lyric = lyrics[idx]
                lyric["t"] = t
                lyrics.sort(key=lambda item: item["t"])
                self.mark_dirty()
                self.checkpoint(f"Moved Lyric to {t:.3f}s")
                self.backend.reset_loop_range()
                new_idx = lyrics.index(lyric)
                return {"idx": new_idx, "lyric": lyric}
            return None

    def move_harmony_flag(self, idx: int, t: float) -> dict | None:
        with self._lock:
            flags = self._flags.harmony_flags
            if 0 <= idx < len(flags):
                flag = flags[idx]
                flag["t"] = t
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()
                self.checkpoint(f"Moved Chord Flag to {t:.3f}s")
                new_idx = flags.index(flag)
                return {"idx": new_idx, "flag": flag}
            return None

    def update_harmony_flag(self, idx: int, t: float, chord: Dict[str, Any]) -> None:
        with self._lock:
            flags = self._flags.harmony_flags
            if 0 <= idx < len(flags):
                flags[idx] = {"t": t, "c": chord}
                flags.sort(key=lambda f: f["t"])
                self.mark_dirty()
                self.checkpoint(f"Updated Chord Flag at {t:.3f}s")

    def move_flag(self, idx: int, t: float) -> dict | None:
        with self._lock:
            flags = self._flags.flags
            if 0 <= idx < len(flags):
                flag = flags[idx]
                flag["t"] = t
                flags.sort(key=lambda f: f["t"])
                self._flags._recompute_auto_names()
                self._clear_backend_cache()
                self.mark_dirty()
                self.checkpoint(f"Moved Rhythm Flag to {t:.3f}s")
                new_idx = flags.index(flag)
                return {"idx": new_idx, "flag": flag}
            return None

    def update_flag(self, idx: int, t: float, kind: str = "rhythm", div: int = 0, n: str = "", s: bool = False, divshade: bool = False) -> None:
        with self._lock:
            flags = self._flags.flags
            if 0 <= idx < len(flags):
                flags[idx] = {"t": t, "type": kind, "div": div, "n": n, "s": s, "divshade": divshade}
                flags.sort(key=lambda f: f["t"])
                self._flags._recompute_auto_names()
                self._clear_backend_cache()
                self.mark_dirty()
                self.checkpoint(f"Updated Rhythm Flag at {t:.3f}s")

    # ---------- playback passthrough ----------
    def seek(self, time: float) -> None: self.backend.seek(time)
    def pause(self) -> None: self.backend.pause()
    def play(self) -> None:
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
            return self._looping.get_loop_range(pos, self.duration, self._flags.flags, self.lyrics, self.selected_lyric_idx)

    # ---------- metronome helpers ----------
    def subdivision_ticks_between(self, start: float, end: float) -> list[tuple[float, bool]]:
        import bisect
        ticks: list[tuple[float, bool]] = []
        with self._lock:
            flags = list(self._flags.flags)

        for i, prev in enumerate(flags):
            if prev.get("type", "rhythm") != "rhythm": continue
            if start <= prev["t"] < end: ticks.append((prev["t"], True))
            if i + 1 < len(flags):
                nxt = flags[i + 1]
                subdiv = prev.get("div", 0)
                if subdiv == 0:
                    for p in reversed(flags[: i + 1]):
                        if p.get("type", "rhythm") == "rhythm" and p.get("div", 0) != 0:
                            subdiv = p["div"]
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
            subdiv = left.get("div", 0)

            added = False
            for i in range(1, count + 1):
                t_new = left["t"] + i * step
                if self._flags.add_flag(t_new, type="rhythm", div=subdiv, n="", s=False, divshade=False) != -1:
                    added = True

            if added:
                self._clear_backend_cache()
                self.mark_dirty()
                self._emit("flag_added", left["t"])
                self.checkpoint(f"Inserted {count} flags")

    def checkpoint(self, label: str) -> None:
        with self._lock:
            data = self._manager._scrub_defaults(self.session_data)
            self._undo.push(label, data)

    def restore_checkpoint(self, index: int) -> None:
        with self._lock:
            new_data = self._undo.restore(index)
            # Update session_data and all managers
            self.session_data.clear()
            self.session_data.update(new_data)
            self._manager._fill_defaults(self.session_data)
            self._flags = FlagManager(self.session_data)
            self._clear_backend_cache()
            self.mark_dirty()
