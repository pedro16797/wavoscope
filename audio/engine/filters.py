from __future__ import annotations
import numpy as np

def butter_4th_order_sos(freq: float, sr: int, btype: str) -> np.ndarray:
    """
    Generate SOS coefficients for a 4th order Butterworth filter.
    btype: 'lowpass' or 'highpass'
    """
    nyquist = sr / 2.0
    f = freq / nyquist

    # Pre-warp
    wa = np.tan(np.pi * f / 2.0)
    wa2 = wa * wa

    # Poles for N=4: angles are 5pi/8 and 7pi/8 from positive real axis?
    # No, standard butterworth poles are s_k = exp(j * (pi/2 + (2k-1)*pi/(2N)))
    # For N=4, k=1,2: angles are 5pi/8 and 7pi/8.
    # Re(p1) = cos(5pi/8) = -sin(pi/8)
    # Re(p2) = cos(7pi/8) = -sin(3pi/8)
    zeta = [np.sin(np.pi / 8.0), np.sin(3.0 * np.pi / 8.0)]

    sos = np.zeros((2, 6))
    for i in range(2):
        z = zeta[i]
        # Denominator coefficients
        a0 = 1.0 + 2.0 * z * wa + wa2
        a1 = 2.0 * (wa2 - 1.0) / a0
        a2 = (1.0 - 2.0 * z * wa + wa2) / a0

        if btype == 'lowpass':
            b0 = wa2 / a0
            b1 = 2.0 * wa2 / a0
            b2 = wa2 / a0
        else: # highpass
            b0 = 1.0 / a0
            b1 = -2.0 / a0
            b2 = 1.0 / a0

        sos[i] = [b0, b1, b2, 1.0, a1, a2]

    return sos

def sosfilt_zi(sos: np.ndarray) -> np.ndarray:
    """
    Construct initial conditions for sosfilt.
    Matches scipy.signal.sosfilt_zi for step response.
    """
    n_sections = sos.shape[0]
    zi = np.zeros((n_sections, 2))

    # For each section, we want the initial state that yields steady state
    # for a unit step input.
    # H(1) = (b0 + b1 + b2) / (1 + a1 + a2)
    # y = b0*x + z1
    # z1 = b1*x - a1*y + z2
    # z2 = b2*x - a2*y
    # => z2 = b2 - a2*y
    # => z1 = b1 - a1*y + b2 - a2*y = (b1+b2) - (a1+a2)*y

    # But wait, each section's output is the input to the next section.
    x = 1.0
    for i in range(n_sections):
        b0, b1, b2, _, a1, a2 = sos[i]
        h1 = (b0 + b1 + b2) / (1.0 + a1 + a2)
        y = h1 * x
        zi[i, 1] = b2 * x - a2 * y
        zi[i, 0] = (b1 * x - a1 * y) + zi[i, 1]
        x = y # Output of this section is input to next

    return zi

def sosfilt(sos: np.ndarray, x: np.ndarray, zi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Filter data using cascaded second-order sections.
    Pure python implementation (slower than scipy but removes dependency).
    """
    y = x.tolist()
    new_zi = zi.copy()
    n_sections = sos.shape[0]

    # Transposed Direct Form II
    for i in range(n_sections):
        b0, b1, b2, _, a1, a2 = sos[i]
        z1, z2 = new_zi[i]

        # Iterating over a list is faster than a numpy array in pure Python loops.
        for n in range(len(y)):
            xn = y[n]
            yn = b0 * xn + z1
            z1 = b1 * xn - a1 * yn + z2
            z2 = b2 * xn - a2 * yn
            y[n] = yn

        new_zi[i] = [z1, z2]

    return np.array(y, dtype=np.float32), new_zi

class FilterEngine:
    def __init__(self, sr: int):
        self._sr = sr
        self._enabled: bool = True
        self._low_enabled: bool = False
        self._high_enabled: bool = False
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

        if self._low_enabled and self._high_enabled:
            # Bandpass: cascade highpass and lowpass
            # (scipy.signal.butter(4, [low, high], 'bandpass') is actually 8th order)
            # We match this by cascading two 4th order filters.
            sos_high = butter_4th_order_sos(self._low_hz, self._sr, 'highpass')
            sos_low = butter_4th_order_sos(self._high_hz, self._sr, 'lowpass')
            self._sos = np.vstack([sos_high, sos_low])
        elif self._low_enabled:
            self._sos = butter_4th_order_sos(self._low_hz, self._sr, 'highpass')
        else:
            self._sos = butter_4th_order_sos(self._high_hz, self._sr, 'lowpass')

        self._zi = sosfilt_zi(self._sos)

    def process(self, chunk: np.ndarray) -> np.ndarray:
        if self._sos is not None and self._zi is not None:
            chunk, self._zi = sosfilt(self._sos, chunk, self._zi)
        return chunk

    def reset_zi(self):
        if self._sos is not None:
            self._zi = sosfilt_zi(self._sos)
