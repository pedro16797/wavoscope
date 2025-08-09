from PySide6.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QKeySequenceEdit, QSlider,
                               QComboBox, QSpinBox, QFormLayout, QPushButton, QKeySequenceEdit, QLabel)
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
from wavoscope.utils.config import Config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.setWindowTitle("Settings")
        self.resize(500, 400)

        tabs = QTabWidget(self)
        global_tab = QWidget()

        form = QFormLayout(global_tab)

        # Theme
        self.theme_cb = QComboBox()
        self.theme_cb.addItems(["dark", "light"])
        self.theme_cb.setCurrentText(self.config.get("ui.theme", "dark"))
        form.addRow("UI Theme:", self.theme_cb)

        # Click volume slider
        self.click_volume = QSlider(Qt.Horizontal)
        self.click_volume.setRange(0, 100)
        self.click_volume.setValue(int(self.config.get("ui.click_volume", 0.3) * 100))
        form.addRow("Click volume:", self.click_volume)
        
        # Ensure proper range
        self.click_volume.setSingleStep(5)

        # Spectrum keys (moved from spectrum tab)
        self.keys_spin = QSpinBox()
        self.keys_spin.setRange(12, 120)
        self.keys_spin.setValue(self.config.get("ui.spectrum_keys", 37))
        form.addRow("Visible piano keys:", self.keys_spin)

        # Keybinds tab
        key_tab = QWidget()
        key_tab.setLayout(QVBoxLayout())
        key_tab.layout().addWidget(KeybindEditor(self.parent().keybinds))

        # Only these two tabs now
        tabs.addTab(global_tab, "Global")
        tabs.addTab(key_tab, "Keybinds")

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)

        lay = QVBoxLayout(self)
        lay.addWidget(tabs)
        lay.addWidget(ok_btn)
        
    def showEvent(self, event):
        super().showEvent(event)
        # Apply theme to tabs and fix header styling
        tab_bar = self.findChild(QTabWidget).tabBar()
        if tab_bar:
            # Make tab headers readable
            tab_bar.setStyleSheet(f"""
                QTabBar::tab {{
                    background: {self.parent().palette().color(self.parent().backgroundRole()).name()};
                    color: {self.parent().palette().color(self.parent().foregroundRole()).name()};
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #555;
                }}
                QTabBar::tab:selected {{
                    background: {self.parent().palette().highlight().color().name()};
                    color: {self.parent().palette().highlightedText().color().name()};
                }}
                QTabBar::tab:hover {{
                    background: {self.parent().palette().mid().color().name()};
                }}
            """)

    def accept(self):
        new_theme = self.theme_cb.currentText()
        self.config.set("ui.theme", new_theme)
        self.config.set("ui.click_volume", self.click_volume.value() / 100.0)
        self.config.set("ui.spectrum_keys", self.keys_spin.value())
        
        if hasattr(self.parent(), 'project') and self.parent().project:
            self.parent().project.backend.set_click_gain(self.click_volume.value() / 100.0)
        
        if hasattr(self.parent(), '_sync_piano_fft'):
            self.parent()._sync_piano_fft()
        
        self.parent()._load_theme(new_theme)
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