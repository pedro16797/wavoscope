import numpy as np
from PySide6.QtCore import Signal, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QPolygonF
from wavoscope.audio.spectrum_analyzer import analyze
from wavoscope.gui.colours import load_palette

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
WHITE = {0, 2, 4, 5, 7, 9, 11}

def midi_to_freq(midi):
    return 440.0 * (2 ** ((midi - 69) / 12.0))

class SpectrumView(QWidget):
    window_changed = Signal(float)
    tone_requested = Signal(float)
    _last_task_pos = None
    _last_task_win = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self._y = None
        self._sr = 44100
        self._position = 0.0
        self._window = 1.0
        self._octave_offset = 0
        self._low_hz = midi_to_freq(48)    # start at C2
        self._high_hz = midi_to_freq(84)   # C5 (3 octaves)
        self._synth = None
        self._pressed = False
        self.setMouseTracking(True)
        self._cached_spectrum = None
        self._last_task_key = None
        self._cache = {}
        self._cache_key = None
        self._cached_result = None

    # ---------- public ----------
    def set_audio_data(self, y, sr):
        self._y = y.astype(np.float32)
        self._sr = sr

    def set_position(self, sec):
        self._position = sec
        # Invalidate cache when position changes significantly
        new_key = (int(sec * 100), int(self._window * 1000))
        if new_key != self._cache_key:
            self._cache_key = new_key
            self._cached_result = None
        self.update()

    def set_fft_window(self, sec):
        self._window = max(sec, 0.05)
        self.window_changed.emit(self._window)
        self.update()

    def set_freq_range(self, low_hz, high_hz):
        self._low_hz = low_hz
        self._high_hz = high_hz
        self.update()

    def set_synth(self, synth):
        self._synth = synth

    # ---------- helpers ----------
    def _hz_at_x(self, x):
        span = np.log2(self._high_hz / self._low_hz)
        if span <= 0:
            return self._low_hz
        return self._low_hz * (2 ** (x * span / self.width()))
    
    def setProject(self, project):
        self.project = project
        self.set_audio_data(self.project._data, self.project._sr)

    # ---------- drawing ----------
    def _on_theme_changed(self, name):
        self.palette = load_palette(name)
        self.update()

    def paintEvent(self, event):
        if (self._y is None or
            not hasattr(self, '_low_hz') or
            self.width() <= 0 or
            not hasattr(self, 'project') or
            self.project is None):
            return

        freqs, db = analyze(
            self._y, self._sr,
            self._position, self._window,
            self._low_hz, self._high_hz,
            self.width()
        )
        if freqs.size == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        h, span_hz = self.height(), max(np.log2(self._high_hz / self._low_hz), 1e-3)
        x_scale = float(self.width()) / span_hz
        low_clip, high_clip = np.percentile(db, [1, 99])
        span_db = max(high_clip - low_clip, 1e-3)

        # grid lines
        low_m = int(np.round(12 * np.log2(self._low_hz / 440) + 69))
        for midi in range(low_m, low_m + 37):
            hz = midi_to_freq(midi)
            x = int(np.log2(hz / self._low_hz) * x_scale + 0.5)
            color = QColor(self.palette["keyWhite"]) if midi % 12 in WHITE else QColor(self.palette["keyBlack"])
            color.setAlpha(128)
            painter.setPen(QPen(color, 3))
            painter.drawLine(x, 0, x, h)
            painter.setPen(QColor(self.palette["text"]))
            painter.drawText(x + 2, 12,
                             f"{NOTE_NAMES[midi % 12]}{(midi - 12) // 12}")

        # spectrum poly-line
        poly = QPolygonF()
        for f, d in zip(freqs, db):
            x = np.log2(f / self._low_hz) * x_scale
            y = h - ((d - low_clip) / span_db) * h
            poly.append(QPointF(x, y))
        painter.setPen(QPen(QColor(self.palette["spectrum"]), 1))
        painter.drawPolyline(poly)
        painter.end()

    # ---------- mouse ----------
    def mousePressEvent(self, event):
        self._pressed = True
        self._play_tone(event.position().x())

    def mouseMoveEvent(self, event):
        if self._pressed:
            self._play_tone(event.position().x())

    def mouseReleaseEvent(self, event):
        self._pressed = False
        if self._synth is not None:
            self._synth.stop_all()

    def _play_tone(self, pos_x):
        if self._synth is None:
            return
        hz = self._hz_at_x(pos_x)
        if hz > 0:
            self._synth.stop_all()
            self._synth.start_tone(hz)

    def leaveEvent(self, event):
        if self._synth is not None:
            self._synth.stop_all()