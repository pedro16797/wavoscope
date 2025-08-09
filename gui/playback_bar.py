"""
Playback control bar: transport buttons, metronome toggle, and sliders for
volume, speed and FFT window.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
)

from wavoscope.gui.colours import load_palette


class PlaybackBar(QWidget):
    # Emitted when the user changes parameters
    volume_changed = Signal(float)       # 0 … 1
    speed_changed = Signal(float)        # 0.1 … 4
    fft_changed = Signal(float)          # seconds
    octave_shift_changed = Signal(int)   # -1/0/+1
    metronome_toggled = Signal(bool)

    @staticmethod
    def _tinted_icon(path: str, color: QColor, size: int = 24) -> QIcon:
        """Return an SVG icon tinted to the requested colour."""
        pm = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p = QPainter(pm)
        p.setCompositionMode(QPainter.CompositionMode_SourceIn)
        p.fillRect(pm.rect(), color)
        p.end()
        return QIcon(pm)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        # ---------- widgets ----------
        self.btn_up = QPushButton()
        self.btn_down = QPushButton()
        self.btn_metronome = QPushButton()
        self.btn_metronome.setCheckable(True)
        self.btn_metronome.setChecked(True)
        self.btn_metronome.setToolTip("Toggle click")

        self.mode_btn = QPushButton("Mode: Rhythm")
        self.btn_play = QPushButton()
        self.btn_stop = QPushButton()

        for btn in (self.btn_up, self.btn_down, self.btn_metronome, self.btn_play, self.btn_stop):
            btn.setFixedSize(32, 32)

        # ---------- time label ----------
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setAlignment(Qt.AlignCenter)

        # ---------- sliders ----------
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(80)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 100)      # mapped 0.1 … 1.0
        self.speed_slider.setValue(100)         # default 1.0
        self.speed_slider.setFixedWidth(80)

        self.fft_slider = QSlider(Qt.Horizontal)
        self.fft_slider.setRange(0, 10)         # 0 … 1 s in 0.1 s steps
        self.fft_slider.setValue(3)             # 0.3 s
        self.fft_slider.setFixedWidth(80)

        # ---------- layout ----------
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(self.btn_down)
        lay.addWidget(self.btn_up)
        lay.addWidget(self.btn_metronome)
        lay.addWidget(self.mode_btn)

        lay.addWidget(self.btn_play)
        lay.addWidget(self.btn_stop)
        lay.addWidget(self.time_label, 1)
        lay.addWidget(QLabel("Vol"))
        lay.addWidget(self.vol_slider)
        lay.addWidget(QLabel("Spd"))
        lay.addWidget(self.speed_slider)
        lay.addWidget(QLabel("FFT"))
        lay.addWidget(self.fft_slider)

        # ---------- wiring ----------
        self.btn_metronome.toggled.connect(self.metronome_toggled)
        self.vol_slider.valueChanged.connect(lambda v: self.volume_changed.emit(v / 100.0))
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_changed.emit(0.1 + (v / 100.0) * 1.9)  # 0.1 … 2.0
        )
        self.fft_slider.valueChanged.connect(lambda v: self.fft_changed.emit(v / 10.0))

    # ---------- public ----------
    def set_position(self, pos: float, duration: float) -> None:
        """Update time display (seconds)."""
        m1, s1 = divmod(int(pos), 60)
        m2, s2 = divmod(int(duration), 60)
        self.time_label.setText(f"{m1}:{s1:02d} / {m2}:{s2:02d}")

    # ---------- theme ----------
    def on_theme_changed(self, name: str) -> None:
        """Recolour icons whenever the palette changes."""
        palette = load_palette(name)
        colour = palette["text"]
        for btn, base_name in (
            (self.btn_play,  "play"),
            (self.btn_stop,  "stop"),
            (self.btn_up,    "arrow-up"),
            (self.btn_down,  "arrow-down"),
            (self.btn_metronome, "metronome"),
        ):
            btn.setIcon(self._tinted_icon(f"./resources/icons/{base_name}.svg", colour))