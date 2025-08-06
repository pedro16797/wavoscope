from PySide6.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QKeySequenceEdit,
                               QComboBox, QSpinBox, QFormLayout, QPushButton, QKeySequenceEdit, QLabel)
from PySide6.QtGui import QKeySequence
from wavoscope.utils.config import Config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.setWindowTitle("Settings")
        self.resize(500, 400)

        tabs = QTabWidget(self)
        global_tab = QWidget()

        # ---------- Spectrum tab ----------
        spectrum_tab = QWidget()
        spec_form = QFormLayout(spectrum_tab)

        self.keys_spin = QSpinBox()
        self.keys_spin.setRange(12, 120)
        self.keys_spin.setValue(self.config.get("ui.spectrum_keys", 37))
        spec_form.addRow("Visible piano keys:", self.keys_spin)

        form = QFormLayout(global_tab)

        self.theme_cb = QComboBox()
        self.theme_cb.addItems(["dark", "light"])
        self.theme_cb.setCurrentText(self.config.get("ui.theme", "dark"))
        form.addRow("UI Theme:", self.theme_cb)

        key_tab = QWidget()
        key_tab.setLayout(QVBoxLayout())
        key_tab.layout().addWidget(KeybindEditor(self.parent().keybinds))

        tabs.addTab(global_tab, "Global")
        tabs.addTab(spectrum_tab, "Spectrum")
        tabs.addTab(key_tab, "Keybinds")

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)

        lay = QVBoxLayout(self)
        lay.addWidget(tabs)
        lay.addWidget(ok_btn)
        
    def showEvent(self, event):
        super().showEvent(event)
        # Apply theme to tabs
        for tab in [self.findChild(QWidget, name) for name in ["global_tab", "spectrum_tab", "key_tab"]]:
            if tab:
                tab.setStyleSheet(self.parent().styleSheet())

    def accept(self):
        new_theme = self.theme_cb.currentText()
        self.config.set("ui.theme", new_theme)
        self.parent()._load_theme(new_theme)
        self.config.set("ui.spectrum_keys", self.keys_spin.value())
        if hasattr(self.parent(), '_sync_piano_fft'):
            self.parent()._sync_piano_fft()
        super().accept()

class KeybindEditor(QWidget):
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        form = QFormLayout(self)
        self._fields = {}
        actions = ["play_pause", "seek_left", "seek_right", "add_harmony_flag", "add_rhythm_flag"]
        for act in actions:
            edit = QKeySequenceEdit(QKeySequence(manager._mapping[act]))
            form.addRow(QLabel(act.replace('_', ' ').title()), edit)
            self._fields[act] = edit
            edit.keySequenceChanged.connect(
                lambda seq, a=act: manager.bind(a, seq.toString())
            )