from __future__ import annotations
import numpy as np
import scipy.signal

class FilterEngine:
    def __init__(self, sr: int):
        self._sr = sr
        self._enabled: bool = False
        self._low_enabled: bool = True
        self._high_enabled: bool = True
        self._low_hz: float = 200.0
        self._high_hz: float = 2000.0
        self._sos: np.ndarray | None = None
        self._zi: np.ndarray | None = None
        self.update_coeffs()

    def set_sr(self, sr: int):
        self._sr = sr
        self.update_coeffs()

    def set_filter(self,
                   enabled: bool | None = None,
                   low: float | None = None,
                   high: float | None = None,
                   low_enabled: bool | None = None,
                   high_enabled: bool | None = None):
        if enabled is not None:
            self._enabled = enabled
        if low_enabled is not None:
            self._low_enabled = low_enabled
        if high_enabled is not None:
            self._high_enabled = high_enabled

        min_gap = 50.0
        new_low = low if low is not None else self._low_hz
        new_high = high if high is not None else self._high_hz

        self._low_hz = max(20.0, min(new_low, new_high - min_gap))
        self._high_hz = max(self._low_hz + min_gap, min(new_high, self._sr / 2 - 20))

        self.update_coeffs()

    def update_coeffs(self):
        if not self._enabled or (not self._low_enabled and not self._high_enabled):
            self._sos = None
            self._zi = None
            return

        nyquist = max(self._sr / 2, 100.0)

        if self._low_enabled and self._high_enabled:
            low = max(10.0, self._low_hz) / nyquist
            high = min(self._high_hz, nyquist - 10.0) / nyquist
            if low >= high:
                low = high * 0.9
            self._sos = scipy.signal.butter(4, [low, high], btype='bandpass', output='sos')
        elif self._low_enabled:
            low = max(10.0, self._low_hz) / nyquist
            self._sos = scipy.signal.butter(4, low, btype='highpass', output='sos')
        else:
            high = min(self._high_hz, nyquist - 10.0) / nyquist
            self._sos = scipy.signal.butter(4, high, btype='lowpass', output='sos')

        self._zi = scipy.signal.sosfilt_zi(self._sos)

    def process(self, chunk: np.ndarray) -> np.ndarray:
        if self._sos is not None and self._zi is not None:
            chunk, self._zi = scipy.signal.sosfilt(self._sos, chunk, zi=self._zi)
        return chunk

    def reset_zi(self):
        if self._sos is not None:
            self._zi = scipy.signal.sosfilt_zi(self._sos)
