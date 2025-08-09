"""
Min-max cache for fast waveform rendering at arbitrary zoom levels.
"""
from __future__ import annotations

from typing import Tuple, List

import numpy as np


class WaveformCache:
    """
    Pre-computes (min, max, intensity) buckets so the GUI can draw
    thousands of vertical bars without touching the raw samples each frame.
    """

    def __init__(self, y: np.ndarray, sr: int) -> None:
        self.y: np.ndarray = y.astype(np.float32)
        self.sr: int = sr
        self._cache: dict[Tuple[int, int], Tuple[float, float]] = {}

    # ---------- public ----------
    def bars(
        self, start_s: float, end_s: float, n_bars: int
    ) -> List[Tuple[float, float, float]]:
        """
        Return [(min_norm, max_norm, intensity), …] for `n_bars`
        covering the given time span.

        `intensity` is derived from crest factor and used for colour modulation.
        """
        if n_bars == 0 or start_s >= end_s:
            return []

        start_idx = max(0, int(start_s * self.sr))
        end_idx = min(len(self.y), int(end_s * self.sr))
        if start_idx >= end_idx:
            return []

        step = max(1, (end_idx - start_idx) // n_bars)
        idx = np.arange(start_idx, end_idx, step, dtype=np.int64)
        ends = np.minimum(idx + step, end_idx)

        # Pre-allocate
        mins = np.empty(len(idx), dtype=np.float32)
        maxs = np.empty(len(idx), dtype=np.float32)
        avgs = np.empty(len(idx), dtype=np.float32)

        for i, (s, e) in enumerate(zip(idx, ends)):
            bucket = self.y[s:e]
            mins[i] = np.min(bucket)
            maxs[i] = np.max(bucket)
            avgs[i] = np.mean(np.abs(bucket))

        # Crest factor -> intensity for colour alpha
        crest = (np.abs(mins) + np.abs(maxs)) * 0.5
        intensity = np.clip(4 * avgs / (1e-12 + crest), 0, 1)
        intensity = (intensity + 2) / 3  # remap 0…1 → 0.66…1

        # Normalise waveform range to [-1, 1]
        low_clip, high_clip = np.percentile(
            self.y[start_idx:end_idx], [0.1, 99.9]
        )
        span = max(high_clip - low_clip, 1e-6)
        mins_norm = (np.clip(mins, low_clip, high_clip) - low_clip) / span * 2 - 1
        maxs_norm = (np.clip(maxs, low_clip, high_clip) - low_clip) / span * 2 - 1

        return list(zip(mins_norm.tolist(), maxs_norm.tolist(), intensity.tolist()))