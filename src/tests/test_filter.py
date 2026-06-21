"""A2: realtime band-pass filter (SciPy-backed, pure-Python fallback)."""
import numpy as np

from audio.engine import filters
from audio.engine.filters import FilterEngine


def _run_blocks(fe: FilterEngine, sig: np.ndarray, block: int = 1024) -> np.ndarray:
    fe.reset_zi()
    out = []
    for i in range(0, len(sig), block):
        out.append(fe.process(sig[i:i + block].copy()))
    return np.concatenate(out)


def test_bandpass_attenuates_out_of_band():
    sr = 44100
    fe = FilterEngine(sr)
    fe.set_filter(enabled=True, low=300.0, high=3000.0,
                  low_enabled=True, high_enabled=True, auto_gain=False)

    t = np.arange(sr, dtype=np.float32) / sr
    inband = np.sin(2 * np.pi * 1000 * t).astype(np.float32)   # passband
    outband = np.sin(2 * np.pi * 50 * t).astype(np.float32)    # well below low cutoff

    y_in = _run_blocks(fe, inband)
    y_out = _run_blocks(fe, outband)

    # Skip the filter transient before measuring steady-state energy.
    rms_in = float(np.sqrt(np.mean(y_in[5000:] ** 2)))
    rms_out = float(np.sqrt(np.mean(y_out[5000:] ** 2)))

    assert rms_in > 0.3                 # in-band passes
    assert rms_out < 0.2 * rms_in       # out-of-band strongly attenuated


def test_scipy_path_matches_pure_python():
    sos = filters.butter_4th_order_sos(1000.0, 44100, "lowpass")
    zi = filters.sosfilt_zi(sos)
    x = np.random.RandomState(0).randn(2048).astype(np.float32)

    y_pure, _ = filters.sosfilt(sos, x, zi.copy())
    y_apply, _ = filters.apply_sos(sos, x, zi.copy())

    assert np.allclose(y_pure, y_apply, atol=1e-3)
