import scipy.fft
import numpy as np

# Cache FFT plans
_fft_plans = {}

def analyze(y, sr, t, window_s, low_hz, high_hz, screen_width):
    half = window_s * 0.7
    start = int(np.clip((t - half) * sr, 0, len(y)))
    end = int(np.clip((t + (window_s - half)) * sr, 0, len(y)))
    n_samples = max(end - start, 64)
    n_fft = 1 << (n_samples - 1).bit_length()
    
    # Use cached plan
    if n_fft not in _fft_plans:
        _fft_plans[n_fft] = scipy.fft.rfft
    
    chunk = y[start:end] * np.hanning(n_samples)
    fft = np.abs(_fft_plans[n_fft](chunk, n=n_fft))
    freqs = scipy.fft.rfftfreq(n_fft, 1 / sr)

    mask = (freqs >= low_hz) & (freqs <= high_hz)
    if not np.any(mask):
        return np.empty(0), np.empty(0)

    f, a = freqs[mask], fft[mask]
    
    # Vectorized dB calculation
    rms = np.sqrt(np.mean(np.square(chunk))) + 1e-12
    db = 20 * np.log10(np.clip(a / rms + 1e-6, 1e-5, 1e6))

    # Efficient downsampling with numpy
    if len(f) > screen_width:
        indices = np.linspace(0, len(f)-1, screen_width, dtype=int)
        return f[indices], db[indices]
    return f, db