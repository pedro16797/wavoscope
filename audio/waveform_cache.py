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
        self.y: np.ndarray = np.asarray(y, dtype=np.float32)
        self.sr: int = sr

        # Pre-calculate percentiles for normalization
        if len(self.y) > 0:
            self.low_clip, self.high_clip = np.percentile(self.y, [0.1, 99.9])
        else:
            self.low_clip, self.high_clip = -1.0, 1.0

    # ---------- public ----------
    def bars(
        self, start_s: float, end_s: float, n_bars: int
    ) -> List[Tuple[float, float, float, float]]:
        """
        Return [(min_norm, max_norm, rms_norm, intensity), …] for `n_bars`
        covering the given time span.

        `intensity` is derived from crest factor and used for colour modulation.
        """
        if n_bars == 0 or start_s >= end_s:
            return []

        start_idx = max(0, int(start_s * self.sr))
        end_idx = min(len(self.y), int(end_s * self.sr))
        if start_idx >= end_idx:
            return []

        # Vectorized bucket calculation
        step = max(1, (end_idx - start_idx) // n_bars)
        indices = np.arange(start_idx, end_idx, step, dtype=np.int64)
        if len(indices) > n_bars:
            indices = indices[:n_bars]

        # Use reduceat for fast min/max/mean
        mins = np.minimum.reduceat(self.y, indices)
        maxs = np.maximum.reduceat(self.y, indices)

        # For mean of absolute values, we use add.reduceat on abs(y)
        abs_y = np.abs(self.y)
        sums_abs = np.add.reduceat(abs_y, indices)
        sums_raw = np.add.reduceat(self.y, indices)

        # Calculate actual bucket sizes for the means
        bucket_sizes = np.diff(np.append(indices, end_idx))
        avgs_abs = sums_abs / bucket_sizes
        avgs_raw = sums_raw / bucket_sizes

        # Crest factor -> intensity for colour alpha
        crest = (np.abs(mins) + np.abs(maxs)) * 0.5
        intensity = np.clip(4 * avgs_abs / (1e-12 + crest), 0, 1)
        intensity = (intensity + 2) / 3  # remap 0…1 → 0.66…1

        # Normalise waveform range to [-1, 1] symmetrically around 0
        limit = max(abs(self.low_clip), abs(self.high_clip), 1e-6)
        mins_norm = np.clip(mins, -limit, limit) / limit
        maxs_norm = np.clip(maxs, -limit, limit) / limit
        means_norm = np.clip(avgs_raw, -limit, limit) / limit

        # RMS (average absolute value) normalized relative to the same limit
        rms_norm = np.clip(avgs_abs / limit, 0, 1)

        return list(zip(mins_norm.tolist(), maxs_norm.tolist(), means_norm.tolist(), rms_norm.tolist(), intensity.tolist()))
