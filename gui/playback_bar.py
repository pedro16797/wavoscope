from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSlider

class PlaybackBar(QWidget):
    volume_changed = Signal(float)
    speed_changed  = Signal(float)
    fft_changed    = Signal(float)
    octave_shift_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)

        self.btn_play = QPushButton("⏵")
        self.btn_play.setFixedSize(32, 32)
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 32)

        self.btn_down = QPushButton("⭳")
        self.btn_up   = QPushButton("⭱")
        for btn in (self.btn_down, self.btn_up):
            btn.setFixedSize(32, 32)
            
        self.mode_btn = QPushButton("Mode: Rhythm")
        self.mode_btn.setFixedHeight(32)

        lay.addWidget(self.btn_down)
        lay.addWidget(self.btn_up)
        lay.addWidget(self.mode_btn)

        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setAlignment(Qt.AlignCenter)

        # volume 0-100
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(80)
        self.vol_slider.valueChanged.connect(lambda v: self.volume_changed.emit(v / 100.0))

        # speed 0.1-4.0
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 100)       # 0.0-1.0
        self.speed_slider.setValue(100)          # 1.0 normal
        self.speed_slider.setFixedWidth(80)
        self.speed_slider.valueChanged.connect(lambda v: self.speed_changed.emit(0.1 + (v / 100.0)))

        # fft window 0.0-2.0 s
        self.fft_slider = QSlider(Qt.Horizontal)
        self.fft_slider.setRange(0, 10)        # 0.0-1.0 in 0.1 steps
        self.fft_slider.setValue(3)           # 0.3 s default
        self.fft_slider.setFixedWidth(80)
        self.fft_slider.valueChanged.connect(lambda v: self.fft_changed.emit(v / 10.0))

        lay.addWidget(self.btn_play)
        lay.addWidget(self.btn_stop)
        lay.addWidget(self.time_label, 1)
        lay.addWidget(QLabel("Vol"))
        lay.addWidget(self.vol_slider)
        lay.addWidget(QLabel("Spd"))
        lay.addWidget(self.speed_slider)
        lay.addWidget(QLabel("FFT"))
        lay.addWidget(self.fft_slider)

    def set_position(self, pos, dur):
        m1, s1 = divmod(int(pos), 60)
        m2, s2 = divmod(int(dur), 60)
        self.time_label.setText(f"{m1}:{s1:02d} / {m2}:{s2:02d}")