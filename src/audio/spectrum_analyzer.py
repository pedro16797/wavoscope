"""
FFT-based spectrum analysis with caching of FFT plans.

Public entry point:
    analyze(y, sr, t, window_s, low_hz, high_hz, screen_width)
→ (freqs, dB)
"""
from __future__ import annotations

from typing import Any, Tuple

import numpy as np
import numpy.fft

# FFT plan cache: n_fft → function
_PLANS: dict[int, Any] = {}


def analyze(
    y: np.ndarray,
    sr: int,
    t: float,
    window_s: float,
    low_hz: float,
    high_hz: float,
    screen_width: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute (down-sampled) magnitude spectrum for one time slice.

    Parameters
    ----------
    y : audio samples
    sr : sample rate
    t : centre time (seconds)
    window_s : total time span analysed
    low_hz, high_hz : frequency band of interest
    screen_width : number of pixels (max points to return)
    """
    half = window_s * 0.7
    start = int(np.clip((t - half) * sr, 0, y.size))
    end = int(np.clip((t + (window_s - half)) * sr, 0, y.size))
    n_samples = max(end - start, 64)
    n_fft = 1 << (n_samples - 1).bit_length()

    # Cached plan
    if n_fft not in _PLANS:
        _PLANS[n_fft] = numpy.fft.rfft

    chunk = y[start:end] * np.hanning(n_samples)
    fft = np.abs(_PLANS[n_fft](chunk, n=n_fft))
    freqs = numpy.fft.rfftfreq(n_fft, 1.0 / sr)

    idx_first = np.searchsorted(freqs, low_hz)
    if idx_first > 0:
        idx_first -= 1
    idx_last = np.searchsorted(freqs, high_hz) + 1

    f, a = freqs[idx_first:idx_last], fft[idx_first:idx_last]
    if f.size == 0:
        return np.empty(0), np.empty(0)

    # dB relative to RMS of the chunk
    rms = np.sqrt(np.mean(np.square(chunk))) + 1e-12
    db = 20 * np.log10(np.clip(a / rms + 1e-6, 1e-5, 1e6))

    # Down-sample to screen width
    if f.size > screen_width:
        idx = np.linspace(0, f.size - 1, screen_width, dtype=int)
        return f[idx], db[idx]
    return f, db