"""
Main application window: menu-bar, playback bar, waveform, spectrum and timeline.
Handles file I/O, keyboard shortcuts and theme switching.
"""
from __future__ import annotations

from pathlib import Path
from typing import cast

from PySide6.QtCore import (
    QEvent,
    QObject,
    QTimer,
    Qt,
    Signal,
)
from PySide6.QtGui import QAction, QKeySequence, QKeyEvent, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from wavoscope.audio.audio_backend import AudioBackend
from wavoscope.gui.colours import full_stylesheet
from wavoscope.gui.playback_bar import PlaybackBar
from wavoscope.gui.spectrum_view import SpectrumView
from wavoscope.gui.timeline import Timeline
from wavoscope.gui.waveform_view import WaveformView
from wavoscope.session.project import Project
from wavoscope.utils.config import Config
from wavoscope.utils.config import AUDIO_FILTER
from wavoscope.utils.keybind_manager import KeybindManager


def _midi_to_freq(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12))


class MainWindow(QMainWindow):
    """Top-level window containing all widgets."""

    theme_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Wavoscope")
        self.setGeometry(100, 100, 1200, 700)

        # ── Core objects ──
        self.project: Project | None = None
        self.config = Config()
        self.keybinds = KeybindManager(self)
        self.keybinds.triggered.connect(self._handle_key_action)

        # ── UI setup ──
        self._build_ui()
        self._build_menu()
        self._load_theme(self.config.get("ui.theme", "dark"))

        # 30 ms ticker to sync widgets
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start(30)
        
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        # 1. Create widgets first
        self.playback_bar = PlaybackBar()
        self.timeline = Timeline()
        self.waveform = WaveformView()
        self.spectrum = SpectrumView()

        # 2. Layout
        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.timeline)
        top_layout.addWidget(self.waveform)

        top = QWidget()
        top.setLayout(top_layout)

        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(self.spectrum)

        bottom = QWidget()
        bottom.setLayout(bottom_layout)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top)
        splitter.addWidget(bottom)

        main_layout = QVBoxLayout(central)
        main_layout.addWidget(self.playback_bar)
        main_layout.addWidget(splitter)

        # 3. Connections now that objects exist
        self.playback_bar.volume_changed.connect(
            lambda v: self.project and self.project.set_volume(v)
        )
        self.playback_bar.speed_changed.connect(
            lambda v: self.project and self.project.set_speed(v)
        )
        self.playback_bar.fft_changed.connect(self.spectrum.set_fft_window)
        self.playback_bar.btn_up.clicked.connect(lambda: self._shift_octave(1))
        self.playback_bar.btn_down.clicked.connect(lambda: self._shift_octave(-1))
        self.playback_bar.metronome_toggled.connect(
            lambda enabled: self.project
            and self.project.backend.set_metronome_enabled(enabled)
        )

        # Sync signals
        self.waveform.viewport_changed.connect(self.timeline.update)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        open_action = QAction("&Open…", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_file_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()
        settings_action = QAction("&Settings…", self)
        settings_action.setShortcut(QKeySequence.Preferences)
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------
    def _open_file_dialog(self) -> None:
        """Show open-file dialog and load selected audio."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", AUDIO_FILTER)
        if not path:
            return

        # Stop current playback cleanly
        if self.project:
            self.project.backend.pause()
            self.project.backend.close()

        # Disconnect old signals to avoid duplicate connections
        if hasattr(self, "_connected") and self._connected:
            try:
                self.waveform.seek_requested.disconnect()
                self.playback_bar.btn_play.clicked.disconnect()
                self.playback_bar.btn_stop.clicked.disconnect()
                self.playback_bar.metronome_toggled.disconnect()
            except RuntimeError:
                pass  # already disconnected
            self._connected = False

        # Create new project
        self.project = Project(Path(path))
        self.project.open_file(Path(path))
        self._connect_project_signals()

        # Feed data to widgets
        self.spectrum.set_project(self.project)
        self.waveform.set_project(self.project)
        self.timeline.set_cursor(0.0)
        self.timeline.set_audio_data(self.project._data, self.project._sr)
        self._sync_piano_fft()
        self.playback_bar.set_position(0.0, self.project.duration)
        self.setWindowTitle(f"Wavoscope – {Path(path).name}")

    def _save_project(self) -> None:
        if self.project:
            self.project.save()

    # ------------------------------------------------------------------
    # Keyboard / keybind handling
    # ------------------------------------------------------------------
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            ke = cast(QKeyEvent, event)
            key = ke.key()
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if event.type() == QEvent.Type.KeyPress and not ke.isAutoRepeat():
                    self._key_dir = key
                    self._key_timer = QTimer(self)
                    self._key_timer.setInterval(50)
                    self._key_timer.timeout.connect(self._handle_hold)
                    self._key_timer.start()
                elif event.type() == QEvent.Type.KeyRelease and not ke.isAutoRepeat():
                    if hasattr(self, "_key_timer"):
                        self._key_timer.stop()
                return True
        return super().eventFilter(obj, event)

    def _handle_key_action(self, action: str) -> None:
        if not self.project:
            return
        if action == "play_pause":
            self._toggle_play()
        elif action == "seek_left":
            self.project.seek(self.project.position - 0.1)
        elif action == "seek_right":
            self.project.seek(self.project.position + 0.1)
        elif action == "save":
            self._save_project()

    def _handle_hold(self) -> None:
        """Repeated seek/speed while arrow keys are held."""
        if not hasattr(self, "_key_dir") or not self.project:
            return
        if self._key_dir == Qt.Key_Left:
            self.project.seek(self.project.position - 0.1)
        elif self._key_dir == Qt.Key_Right:
            self.project.seek(self.project.position + 0.1)
        elif self._key_dir == Qt.Key_Up:
            self.project.set_speed(min(4.0, self.project.backend._speed + 0.1))
        elif self._key_dir == Qt.Key_Down:
            self.project.set_speed(max(0.1, self.project.backend._speed - 0.1))

    # ------------------------------------------------------------------
    # Playback helpers
    # ------------------------------------------------------------------
    def _toggle_play(self) -> None:
        if not self.project:
            return
        if self.project.backend._playing:
            self.project.pause()
        else:
            self.project.play()

    def _shift_octave(self, delta: int) -> None:
        """Move visible octave up/down."""
        self._octave_offset = getattr(self, "_octave_offset", 0) + delta
        self._sync_piano_fft()

    def _sync_piano_fft(self) -> None:
        """Re-calculate FFT frequency range for piano keys."""
        base = 48 + getattr(self, "_octave_offset", 0) * 12
        visible_keys = int(self.config.get("ui.spectrum_keys", 37))
        self.spectrum.set_freq_range(
            _midi_to_freq(base), _midi_to_freq(base + visible_keys - 1)
        )

    # ------------------------------------------------------------------
    # Theme & settings
    # ------------------------------------------------------------------
    def _load_theme(self, name: str) -> None:
        """Apply stylesheet and propagate to children."""
        self.setStyleSheet(full_stylesheet(name))
        for widget in (
            self.playback_bar,
            self.waveform,
            self.timeline,
            self.spectrum,
        ):
            widget.setStyleSheet(full_stylesheet(name))
        self.theme_changed.emit(name)

    def _show_settings(self) -> None:
        """Open settings modal."""
        from wavoscope.gui.dialogs.settings import SettingsDialog

        SettingsDialog(self).exec()

    def _connect_project_signals(self) -> None:
        """Wire project backend to GUI."""
        if not hasattr(self, "_connected") or not self._connected:
            self.waveform.seek_requested.connect(self.project.seek)
            self.project.backend.set_tick_provider(self.project.subdivision_ticks_between)
            self.playback_bar.btn_play.clicked.connect(self.project.play)
            self.playback_bar.btn_stop.clicked.connect(self.project.pause)

            # Initial click volume
            click_vol = self.config.get("ui.click_volume", 0.5)
            self.project.backend.set_click_gain(click_vol)

            # Theme hooks
            self.theme_changed.connect(self.playback_bar.on_theme_changed)
            self.theme_changed.connect(self.timeline._on_theme_changed)
            self.theme_changed.connect(self.spectrum._on_theme_changed)
            self.theme_changed.connect(self.waveform._on_theme_changed)

            self._connected = True

    # ------------------------------------------------------------------
    # House-keeping
    # ------------------------------------------------------------------
    def _on_tick(self) -> None:
        """30 ms update loop to keep widgets in sync."""
        if not self.project or self.project._data is None:
            return

        pos = self.project.position
        dur = self.project.duration
        self.playback_bar.set_position(pos, dur)
        self.timeline.set_cursor(pos)
        self.waveform.set_cursor(pos)
        self.spectrum.set_position(pos)

    def closeEvent(self, event) -> None:
        if self.project and self.project._dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Save:
                self._save_project()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()