from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QEvent, QObject, Signal
from PySide6.QtGui import QShortcut, QKeyEvent, QKeySequence
from wavoscope.utils.config import Config

class KeybindManager(QObject):
    triggered = Signal(str)          # action_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._shortcuts = {}
        self._mapping = {}
        self.config = Config()
        self._load_defaults()
        self._install_shortcuts()

    # ---------- public ----------
    def bind(self, action_id: str, key_sequence: str):
        """Change binding at runtime & persist."""
        self._mapping[action_id] = key_sequence
        self.config.set(f"ui.keybinds.{action_id}", key_sequence)
        self._rebuild()

    def reset(self, action_id: str):
        """Reset to default.json value."""
        from pathlib import Path
        import json
        defaults = json.loads(Path(__file__).with_name("../../config/default.json").read_text())
        default_key = (
            defaults.get("ui", {})
                   .get("keybinds", {})
                   .get(action_id, "")
        )
        self.bind(action_id, default_key)

    # ---------- internal ----------
    def _load_defaults(self):
        schema = {
            "play_pause": "Space",
            "seek_left": "Left",
            "seek_right": "Right",
            "add_harmony_flag": "H",
            "add_rhythm_flag": "R",
        }
        for action, default in schema.items():
            self._mapping[action] = self.config.get(f"ui.keybinds.{action}", default)

    def _install_shortcuts(self):
        for action, seq in self._mapping.items():
            if seq:
                sc = QShortcut(QKeySequence(seq), self.parent())
                sc.activated.connect(lambda _=None, a=action: self.triggered.emit(a))
                self._shortcuts[action] = sc

    def _rebuild(self):
        for sc in self._shortcuts.values():
            sc.setEnabled(False)
            sc.deleteLater()
        self._shortcuts.clear()
        self._install_shortcuts()