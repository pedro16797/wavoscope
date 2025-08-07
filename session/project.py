from pathlib import Path
from PySide6.QtCore import QObject, Signal
import json
from wavoscope.audio.audio_backend import AudioBackend
from wavoscope.audio.waveform_cache import WaveformCache

class Project(QObject):
    flag_added = Signal(float)
    flag_removed = Signal(int)

    # --------- playback passthrough ---------
    def seek(self, t):            self.backend.seek(t)
    def play(self):               self.backend.play()
    def pause(self):              self.backend.pause()
    @property
    def flags(self) -> list[dict]: return self.session_data.setdefault("flags", [])
    @property
    def _data(self): return self.backend._data
    @property
    def duration(self): return self.backend.duration
    @property
    def position(self): return self.backend.position
    @property
    def _sr(self): return self.backend._sr

    def __init__(self, audio_path: Path):
        super().__init__()
        self.audio_path = audio_path
        self.sidecar_path = audio_path.with_suffix(audio_path.suffix + "oscope")
        self.backend = AudioBackend()
        self.session_data = self._load_or_create_sidecar()
        self._spectrum_cache = {}
        self.wave_cache = None

    def _load_or_create_sidecar(self):
        if self.sidecar_path.exists():
            return json.loads(self.sidecar_path.read_text())
        return {"labels": [], "loopPoints": [], "lastView": {}}

    def save(self):
        self.sidecar_path.write_text(json.dumps(self.session_data, indent=2))

    def open_file(self, path: Path):
        # Stop and cleanup any existing playback
        if self.backend._playing:
            self.backend.pause()
        self.backend.close()
        
        # Clear caches
        self._spectrum_cache.clear()
        self.wave_cache = None
        
        # Load new file
        self.backend.open_file(path)
        self.wave_cache = WaveformCache(self.backend._data, self.backend._sr)

    def add_flag(self, t: float, type_: str = "rhythm", subdivision: int = 0,
                 name: str = "", is_section_start: bool = False):
        if any(abs(f["t"] - t) < 0.001 for f in self.flags):
            return
        self.flags.append({
            "t": t,
            "type": type_,
            "subdivision": subdivision,
            "name": name,
            "is_section_start": is_section_start,
        })
        self.flags.sort(key=lambda f: f["t"])
        self._recompute_auto_names()
        self.save()
        self.flag_added.emit(t)

    def remove_flag(self, idx: int):
        self.flags.pop(idx)
        self._recompute_auto_names()
        self.save()
        self.flag_removed.emit(idx)

    def move_flag(self, idx: int, new_time: float):
        if 0 <= idx < len(self.flags):
            self.flags[idx]["t"] = new_time
            self._recompute_auto_names()
            self.save()

    def set_speed(self, speed: float):
        self.backend.set_speed(speed)

    def set_volume(self, volume: float):
        self.backend.set_volume(volume)

    def subdivision_ticks_between(self, t_start, t_end):
        ticks = []
        for prev, nxt in zip(self.flags, self.flags[1:]):
            if prev["type"] != "rhythm":
                continue
            span = nxt["t"] - prev["t"]
            subdiv = prev.get("subdivision", 0)
            if subdiv == 0:
                for p in reversed(self.flags[:self.flags.index(prev)+1]):
                    if p["type"] == "rhythm" and p.get("subdivision", 0) != 0:
                        subdiv = p["subdivision"]
                        break
                else:
                    subdiv = 1
            if subdiv <= 1:
                ticks.append((prev["t"], True))
            else:
                step = span / subdiv
                for k in range(subdiv):
                    tick_t = prev["t"] + k * step
                    if t_start <= tick_t < t_end:
                        is_strong = (k == 0)
                        ticks.append((tick_t, is_strong))
        return sorted(ticks, key=lambda x: x[0])

    def _recompute_auto_names(self):
        """
        Re-apply auto names to rhythm flags.
        Section starts: A, B, C …
        Measures inside section: A-01, A-02 …
        """
        section_idx = 0
        measure_counter = 0
        for f in self.flags:
            if f["type"] != "rhythm":
                continue

            if f.get("is_section_start", False):
                section_name = chr(ord("A") + section_idx)
                section_idx += 1
                measure_counter = 0
                f["name"] = section_name
            else:
                measure_counter += 1
                section_name = chr(ord("A") + section_idx - 1) if section_idx else ""
                f["name"] = f"{section_name}-{measure_counter:02d}"