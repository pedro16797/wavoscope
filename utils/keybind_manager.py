"""
Runtime key-binding manager.

Signals
-------
triggered(action_id: str)   # emitted when a bound shortcut is activated
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut

from wavoscope.utils.config import Config

_DEFAULT_FILE: Path = Path(__file__).with_suffix("") / "../../config/default.json"


class KeybindManager(QObject):
    triggered = Signal(str)  # action_id

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._shortcuts: Dict[str, QShortcut] = {}
        self._mapping: Dict[str, str] = {}  # action -> QKeySequence string
        self._config = Config()
        self._load_schema()
        self._rebuild()

    # ---------- public ----------
    def bind(self, action: str, sequence: str) -> None:
        """Change a binding at runtime and persist it."""
        self._mapping[action] = sequence
        self._config.set(f"ui.keybinds.{action}", sequence)
        self._rebuild()

    def reset(self, action: str) -> None:
        """Revert one action to the factory default."""
        default = self._schema.get(action, "")
        self.bind(action, default)

    # ---------- internal ----------
    def _load_schema(self) -> None:
        """Load factory defaults from default.json."""
        with _DEFAULT_FILE.open() as fp:
            raw = json.load(fp)
        self._schema = raw.get("ui", {}).get("keybinds", {})

        for action, default in self._schema.items():
            self._mapping[action] = self._config.get(f"ui.keybinds.{action}", default)

    def _rebuild(self) -> None:
        """Destroy and recreate QShortcuts to match current mapping."""
        # Clean up existing shortcuts
        for sc in self._shortcuts.values():
            sc.setEnabled(False)
            sc.deleteLater()
        self._shortcuts.clear()

        # Create new ones
        for action, seq in self._mapping.items():
            if not seq:
                continue
            shortcut = QShortcut(QKeySequence(seq), self.parent())
            shortcut.activated.connect(
                lambda _=None, a=action: self.triggered.emit(a)
            )
            self._shortcuts[action] = shortcut