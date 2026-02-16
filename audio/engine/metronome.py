from __future__ import annotations
import bisect
from typing import Callable, List, Tuple
import numpy as np

class MetronomeEngine:
    def __init__(self, sr: int):
        self._sr = sr
        self._click_volume: float = 0.3
        self._strong_freq: float = 1200.0
        self._weak_freq: float = 800.0
        self._metronome_enabled: bool = True
        self._strong_click = np.zeros(0, dtype=np.float32)
        self._weak_click = np.zeros(0, dtype=np.float32)
        self.precalculate_clicks()

    def set_sr(self, sr: int):
        self._sr = sr
        self.precalculate_clicks()

    def set_volume(self, volume: float):
        self._click_volume = max(0.0, min(volume, 1.0))
        self.precalculate_clicks()

    def set_enabled(self, enabled: bool):
        self._metronome_enabled = enabled

    def precalculate_clicks(self):
        dur_s = 0.1
        click_dur = int(dur_s * self._sr)
        t = np.arange(click_dur) / self._sr
        envelope = np.exp(-t * 20)

        def gen_click(freq: float) -> np.ndarray:
            fundamental = np.sin(2 * np.pi * freq * t)
            harmonic = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            return ((fundamental + harmonic) * envelope).astype(np.float32)

        self._strong_click = gen_click(self._strong_freq)
        self._weak_click = gen_click(self._weak_freq)

    def add_clicks(self, outdata: np.ndarray, frames: int, cursor: float, provider: Callable):
        if not self._metronome_enabled or provider is None:
            return

        callback_start = cursor
        callback_end = cursor + frames / self._sr

        ticks = provider(callback_start, callback_end)

        for tick_time, is_strong in ticks:
            if tick_time < callback_start or tick_time >= callback_end:
                continue

            offset = int((tick_time - callback_start) * self._sr)
            if offset < 0 or offset >= frames:
                continue

            shaded = False
            if hasattr(provider, "__self__"):
                project = getattr(provider, "__self__")
                flags = project.flags
                if flags:
                    times = [f["t"] for f in flags]
                    idx = bisect.bisect_right(times, tick_time) - 1

                    if 0 <= idx < len(flags) - 1:
                        prev = flags[idx]
                        nxt = flags[idx + 1]
                        if prev.get("type") == "rhythm":
                            subdiv = prev.get("subdivision", 1)
                            if subdiv > 1:
                                span = nxt["t"] - prev["t"]
                                step = span / subdiv
                                k = int((tick_time - prev["t"] + 1e-6) / step)
                                shaded = prev.get("shaded_subdivisions", False) and k % 2 == 1

            volume = self._click_volume * (0.5 if shaded else 1.0)
            click_src = self._strong_click if is_strong else self._weak_click

            click_dur = min(len(click_src), frames - offset)
            if click_dur > 0:
                outdata[offset : offset + click_dur, 0] += click_src[:click_dur] * volume
