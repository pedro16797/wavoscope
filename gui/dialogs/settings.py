"""
Modal settings dialog with two tabs:

• Global: theme, click volume, visible piano keys  
• Keybinds: live-editable keyboard shortcuts
"""
from __future__ import annotations

from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QSlider,
    QPushButton,
    QKeySequenceEdit,
)

from wavoscope.utils.config import Config
from wavoscope.gui.colours import AVAILABLE_THEMES


class SettingsDialog(QDialog):
    """Main settings window (modal)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 400)

        self._config = Config()

        self._tabs = QTabWidget(self)
        self._build_global_tab()
        self._build_keybinds_tab()

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self._tabs)
        layout.addWidget(ok_btn)

    # ---------- tab construction ----------
    def _build_global_tab(self) -> None:
        tab = QWidget()
        form = QFormLayout(tab)

        # Theme
        self._theme_cb = QComboBox()
        self._theme_cb.addItems(AVAILABLE_THEMES)
        self._theme_cb.setCurrentText(self._config.get("ui.theme", "dark"))
        form.addRow("UI Theme:", self._theme_cb)

        # Click volume
        self._click_vol = QSlider(Qt.Horizontal)
        self._click_vol.setRange(0, 100)
        self._click_vol.setValue(int(self._config.get("ui.click_volume", 0.3) * 100))
        form.addRow("Click volume:", self._click_vol)

        # Visible piano keys
        self._keys_spin = QSpinBox()
        self._keys_spin.setRange(12, 120)
        self._keys_spin.setValue(self._config.get("ui.spectrum_keys", 37))
        form.addRow("Visible piano keys:", self._keys_spin)

        self._tabs.addTab(tab, "Global")

    def _build_keybinds_tab(self) -> None:
        manager = self.parent().keybinds
        editor = KeybindEditor(manager, self)
        self._tabs.addTab(editor, "Keybinds")

    # ---------- apply & persist ----------
    def accept(self) -> None:
        """Store changed settings and notify parent to reload."""
        new_theme = self._theme_cb.currentText()
        self._config.set("ui.theme", new_theme)

        click_volume = self._click_vol.value() / 100.0
        self._config.set("ui.click_volume", click_volume)

        keys = self._keys_spin.value()
        self._config.set("ui.spectrum_keys", keys)

        parent = cast(QWidget, self.parent())
        if hasattr(parent, "project") and parent.project:
            parent.project.backend.set_click_gain(click_volume)

        if hasattr(parent, "_sync_piano_fft"):
            parent._sync_piano_fft()

        parent._load_theme(new_theme)
        super().accept()


class KeybindEditor(QWidget):
    """Inline widget for live key-binding editing."""

    def __init__(self, manager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager

        form = QFormLayout(self)
        self._edits = {}

        for action in ("play_pause", "seek_left", "seek_right", "add_harmony_flag", "add_rhythm_flag"):
            edit = QKeySequenceEdit(QKeySequence(manager._mapping[action]))
            edit.keySequenceChanged.connect(
                lambda seq, a=action: manager.bind(a, seq.toString())
            )
            form.addRow(action.replace("_", " ").title(), edit)
            self._edits[action] = edit