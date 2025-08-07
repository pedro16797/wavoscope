from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QObject, Signal
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QFileDialog, QSplitter)
from PySide6.QtGui import QAction, QKeySequence, QKeyEvent
from wavoscope.gui.waveform_view import WaveformView
from wavoscope.gui.spectrum_view import SpectrumView
from wavoscope.gui.playback_bar import PlaybackBar
from wavoscope.gui.timeline import Timeline
from wavoscope.utils.helpers import AUDIO_FILTER
from wavoscope.gui.dialogs.settings import SettingsDialog
from wavoscope.session.project import Project
from wavoscope.gui.colours import full_stylesheet, load_theme
from wavoscope.utils.config import Config
from wavoscope.utils.keybind_manager import KeybindManager

def midi_to_freq(midi):
    return 440.0 * (2 ** ((midi - 69) / 12))

class MainWindow(QMainWindow):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wavoscope")
        self.setGeometry(100, 100, 1200, 700)
        self.project = None
        self._update_timer = QTimer(self)          # rename to avoid confusion
        self._update_timer.setInterval(30)
        self._update_timer.timeout.connect(self._on_tick)
        self._update_timer.start()

        # Config
        self.config = Config()
        if "ui.theme" not in self.config._settings.allKeys():
            self.config.set("ui.theme", "dark")
        self.setStyleSheet(full_stylesheet(self.config.get("ui.theme", "dark")))
        self.keybinds = KeybindManager(self)
        self.keybinds.triggered.connect(self._handle_key_action)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        self.playback_bar = PlaybackBar()
        lay.addWidget(self.playback_bar)

        # Splitter
        splitter = QSplitter(Qt.Vertical)
        lay.addWidget(splitter)

        # Top half: Timeline + Waveform
        top = QWidget()
        tv = QVBoxLayout(top)
        tv.setContentsMargins(0, 0, 0, 0)
        self.timeline = Timeline()
        tv.addWidget(self.timeline)
        self.waveform = WaveformView()
        tv.addWidget(self.waveform)
        splitter.addWidget(top)

        # Bottom half: Spectrum + Piano
        bottom = QWidget()
        bv = QVBoxLayout(bottom)
        bv.setContentsMargins(0, 0, 0, 0)
        self.spectrum = SpectrumView()
        bv.addWidget(self.spectrum)
        splitter.addWidget(bottom)

        # Menu
        self._build_menu()

        # Wire events
        self.playback_bar.volume_changed.connect(lambda v: self.project.set_volume(v))
        self.playback_bar.speed_changed.connect(lambda v: self.project.set_speed(v))
        self.playback_bar.fft_changed.connect(lambda v: self.spectrum.set_fft_window(v))
        self.playback_bar.btn_up.clicked.connect(lambda: self._shift_octave(1))
        self.playback_bar.btn_down.clicked.connect(lambda: self._shift_octave(-1))
        self.playback_bar.octave_shift_changed.connect(self._shift_octave)
        self.waveform.viewport_changed.connect(self.timeline.update)
        self._octave_offset = 0
        self._sync_piano_fft()

        # Connect theme change
        self.theme_changed.connect(self.timeline._on_theme_changed)
        self.theme_changed.connect(self.spectrum._on_theme_changed)
        self.theme_changed.connect(self.waveform._on_theme_changed)
        self._load_theme(self.config.get("ui.theme", "dark"))

    def _connect_project_signals(self):
        if not hasattr(self, '_connected') or not self._connected:
            self.waveform.seek_requested.connect(self.project.seek)
            self.project.backend.set_tick_provider(self.project.subdivision_ticks_between)
            self.playback_bar.btn_play.clicked.connect(self.project.play)
            self.playback_bar.btn_stop.clicked.connect(self.project.pause)
            self.playback_bar.mode_btn.clicked.connect(
                lambda: self.timeline._on_mode_clicked())
            self._connected = True

    # ---------- UI / menu ----------
    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        open_action = QAction("&Open…", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()
        settings_action = QAction("&Settings…", self)
        settings_action.setShortcut(QKeySequence.Preferences)
        settings_action.triggered.connect(lambda: SettingsDialog(self).exec())
        file_menu.addAction(settings_action)

    def _load_theme(self, name):
        self.setStyleSheet(full_stylesheet(name))
        for w in (self.playback_bar, self.waveform, self.timeline, self.spectrum):
            w.setStyleSheet(full_stylesheet(name))
        self.theme_changed.emit(name)

    # ---------- Keyboard seek / speed ----------
    def eventFilter(self, obj: QObject, event):
        # only key events carry a key()
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            ke = QKeyEvent(event)          # cast to key event
            key = ke.key()
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if event.type() == QEvent.Type.KeyPress and not ke.isAutoRepeat():
                    self._key_dir = key
                    self._key_timer = QTimer(self)
                    self._key_timer.setInterval(50)
                    self._key_timer.timeout.connect(self._handle_hold)
                    self._key_timer.start()
                elif event.type() == QEvent.Type.KeyRelease and not ke.isAutoRepeat():
                    if hasattr(self, '_key_timer'):
                        self._key_timer.stop()
                return True
        return super().eventFilter(obj, event)

    def _handle_hold(self):
        # same logic as before
        if self._key_dir == Qt.Key_Left:
            self.project.seek(self.project.position - 0.1)
        elif self._key_dir == Qt.Key_Right:
            self.project.seek(self.project.position + 0.1)
        elif self._key_dir == Qt.Key_Up:
            self.project.set_speed(self.project._speed + 0.1)
        elif self._key_dir == Qt.Key_Down:
            self.project.set_speed(max(0.1, self.project._speed - 0.1))

    def _handle_key_action(self, action: str):
        if self.project is None:
            return
        if action == "play_pause":
            self._toggle_play()
        elif action == "seek_left":
            self.project.seek(self.project.position - 0.1)
        elif action == "seek_right":
            self.project.seek(self.project.position + 0.1)

    # ---------- File ----------
    def _open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open audio", "", AUDIO_FILTER)
        if not path:
            return
        self.project = Project(Path(path))
        self.project.open_file(Path(path))
        self._connect_project_signals()
        self.spectrum.setProject(self.project)
        self.waveform.setProject(self.project)
        self.waveform.set_audio_data(self.project._data, self.project._sr)
        self.waveform.set_viewport_range(0, self.project.duration)
        self.timeline.set_cursor(0.0)
        self.timeline.set_audio_data(self.project._data, self.project._sr)
        self.timeline.update()
        self._sync_piano_fft()
        self.spectrum.set_audio_data(self.project._data, self.project._sr)
        self.spectrum.set_synth(self.project.backend._synth)
        self.playback_bar.set_position(0, self.project.duration)

    # ---------- Playback ----------
    def _toggle_play(self):
        if self.project.backend._playing:
            self.project.backend.pause()
        else:
            self.project.backend.play()

    def _on_stop(self):
        self.project.pause()
        self.project.seek(0.0)

    def _shift_octave(self, delta):
        self._octave_offset += delta
        self._sync_piano_fft()

    def _sync_piano_fft(self):
        base = 48 + self._octave_offset * 12
        self._low_midi  = base
        visible_keys = int(self.config.get("ui.spectrum_keys", 37))
        self._high_midi = base + visible_keys - 1

        low_hz  = midi_to_freq(self._low_midi)
        high_hz = midi_to_freq(self._high_midi)
        self.spectrum.set_freq_range(low_hz, high_hz)

    # ---------- Update widgets ----------
    def _on_tick(self):
        if self.project is None or self.project._data is None:
            return
        pos = self.project.position
        dur = self.project.duration
        
        # Force sync between waveform and timeline
        view_start = self.waveform._offset
        view_end = view_start + self.waveform.width() / max(self.waveform._zoom * self.waveform._sr, 1)
        
        self.playback_bar.set_position(pos, dur)
        self.timeline.set_cursor(pos)
        self.waveform.set_cursor(pos)
        self.spectrum.set_position(pos)
        
        # Ensure timeline updates when waveform changes
        self.timeline.update()