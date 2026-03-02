from __future__ import annotations
import bisect
from typing import Callable, List, Tuple, Dict, Any
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
        self._active_clicks: List[Dict[str, Any]] = []
        self._last_t: float = -1.0
        self.precalculate_clicks()

    def reset(self):
        self._active_clicks.clear()
        self._last_t = -1.0

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

        # 1ms attack, k=100 decay (~10ms time constant)
        attack_s = 0.001
        attack_len = int(attack_s * self._sr)
        envelope = np.ones(click_dur, dtype=np.float32)
        if attack_len > 0:
            envelope[:attack_len] = np.linspace(0, 1, attack_len)

        decay_k = 100
        envelope[attack_len:] = np.exp(-(t[attack_len:] - attack_s) * decay_k)

        def gen_click(freq: float) -> np.ndarray:
            # Multi-harmonic timbre for a more percussive "woodblock" feel
            wave = (
                1.0 * np.sin(2 * np.pi * freq * t) +
                0.5 * np.sin(2 * np.pi * freq * 2 * t) +
                0.3 * np.sin(2 * np.pi * freq * 3 * t) +
                0.1 * np.sin(2 * np.pi * freq * 4 * t)
            ).astype(np.float32)

            # Simple percussive click via envelope
            click = wave * envelope

            # Normalize to 1.0 peak
            peak = np.max(np.abs(click))
            if peak > 0:
                click /= peak

            return click.astype(np.float32)

        self._strong_click = gen_click(self._strong_freq)
        self._weak_click = gen_click(self._weak_freq)

    def add_clicks(self, outdata: np.ndarray, frames: int, cursor: float, provider: Callable, speed: float = 1.0):
        if not self._metronome_enabled or provider is None:
            self.reset()
            return

        if self._last_t < 0:
            self._last_t = cursor

        callback_start = cursor
        # The timeline covered by 'frames' output samples is (frames / sr) * speed
        callback_end = cursor + (frames / self._sr) * speed

        # 1. Detect new ticks in this callback window.
        # We start searching from the end of the previous callback to prevent double-triggering
        # even if the audio cursor hasn't advanced perfectly due to stalls.
        search_start = self._last_t
        ticks = provider(search_start, callback_end)

        for tick_time, is_strong in ticks:
            if tick_time < search_start or tick_time >= callback_end:
                continue

            # Offset in output samples = (time_until_tick / speed) * sr
            offset = int(((tick_time - callback_start) / speed) * self._sr)
            if offset < 0 or offset >= frames:
                continue

            shaded = False
            if hasattr(provider, "__self__"):
                backend_or_project = getattr(provider, "__self__")
                flags = getattr(backend_or_project, "flags", [])
                if flags:
                    times = [f["t"] for f in flags]
                    idx = bisect.bisect_right(times, tick_time) - 1

                    if 0 <= idx < len(flags) - 1:
                        prev = flags[idx]
                        nxt = flags[idx + 1]
                        if prev.get("type", "rhythm") == "rhythm":
                            subdiv = prev.get("div", 1)
                            if subdiv > 1:
                                span = nxt["t"] - prev["t"]
                                step = span / subdiv
                                k = int((tick_time - prev["t"] + 1e-6) / step)
                                shaded = prev.get("divshade", False) and k % 2 == 1

            volume = self._click_volume * (0.5 if shaded else 1.0)
            click_src = self._strong_click if is_strong else self._weak_click
            self._active_clicks.append({
                "data": click_src * volume,
                "pos": 0,
                "offset": offset
            })

        # 2. Mix all active clicks into the output buffer
        still_active = []
        for click in self._active_clicks:
            data = click["data"]
            pos = click["pos"]
            offset = click["offset"]

            remaining_in_out = frames - offset
            remaining_in_click = len(data) - pos
            chunk_len = min(remaining_in_out, remaining_in_click)

            if chunk_len > 0:
                outdata[offset : offset + chunk_len, 0] += data[pos : pos + chunk_len]
                click["pos"] += chunk_len
                click["offset"] = 0  # Subsequent callbacks start from the beginning of the buffer

            if click["pos"] < len(data):
                still_active.append(click)

        self._active_clicks = still_active
        self._last_t = callback_end
