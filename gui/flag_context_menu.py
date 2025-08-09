"""
Reusable context-menu and modal dialog for editing or inserting flags.
"""
from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QDialogButtonBox,
)
from PySide6.QtGui import QPalette

if TYPE_CHECKING:
    from wavoscope.session.project import Project


class FlagDialog(QDialog):
    """Modal editor for an existing or new flag."""

    def __init__(
        self,
        parent=None,
        project: Project | None = None,
        idx: int | None = None,
        snap_fn: Callable[[float], float] | None = None,
    ) -> None:
        super().__init__(parent)
        self.project = project
        self.flag_idx = idx
        self.flag = project.flags[idx] if idx is not None else None
        self.snap_fn = snap_fn or (lambda t: round(t * 1000) / 1000)

        self.setWindowTitle("Edit Flag")
        self.setModal(True)
        self.setStyleSheet(
            """
            QLabel { border: none; padding: 0; margin: 0; }
            QCheckBox { border: none; padding: 0; margin: 0; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- Name ---
        layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(self.flag.get("name", "") if self.flag else "")
        self.name_edit.setStyleSheet("border: 1px solid #555; padding: 4px;")
        layout.addWidget(self.name_edit)

        # --- Time ---
        layout.addWidget(QLabel("Time:"))
        self.time_edit = QDoubleSpinBox()
        self.time_edit.setDecimals(3)
        self.time_edit.setRange(0, self.project.duration if self.project else 9999)
        self.time_edit.setValue(self.flag["t"] if self.flag else 0.0)
        self.time_edit.setStyleSheet("border: 1px solid #555; padding: 2px;")
        layout.addWidget(self.time_edit)

        # --- Subdivision ---
        layout.addWidget(QLabel("Subdivision:"))
        self.subdiv_edit = QSpinBox()
        self.subdiv_edit.setRange(0, 32)
        self.subdiv_edit.setValue(self.flag.get("subdivision", 0) if self.flag else 0)
        self.subdiv_edit.setStyleSheet("border: 1px solid #555; padding: 2px;")
        layout.addWidget(self.subdiv_edit)

        # --- Check-boxes ---
        self.section_check = QCheckBox("Section start")
        self.section_check.setChecked(self.flag.get("is_section_start", False) if self.flag else False)
        layout.addWidget(self.section_check)

        self.shade_check = QCheckBox("Shade 8th notes")
        self.shade_check.setChecked(self.flag.get("shaded_subdivisions", False) if self.flag else False)
        layout.addWidget(self.shade_check)

        # --- Insert-N button (only between existing flags) ---
        if self.flag_idx is not None:
            next_idx = self.flag_idx + 1
            if next_idx < len(self.project.flags):
                insert_btn = QPushButton("Insert N flags…")
                insert_btn.clicked.connect(self._insert_flags_dialog)
                layout.addWidget(insert_btn)

        layout.addSpacing(8)

        # --- Actions row ---
        buttons_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(
            """
            QPushButton {
                font-weight: bold; background-color: #ff4444; color: white;
                border: 1px solid #555; padding: 8px 4px; min-height: 16px;
            }
            QPushButton:hover { background-color: #ff6666; }
            """
        )
        delete_btn.clicked.connect(self._delete_flag)
        buttons_layout.addWidget(delete_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)

        for i in range(3):
            buttons_layout.setStretch(i, 1)

        layout.addLayout(buttons_layout)

    # ---------- callbacks ----------
    def accept(self) -> None:
        """Save edits and notify project."""
        if self.flag is None:
            return  # should not happen

        self.flag["name"] = self.name_edit.text()
        self.flag["t"] = self.snap_fn(self.time_edit.value())
        self.flag["subdivision"] = self.subdiv_edit.value()
        self.flag["is_section_start"] = self.section_check.isChecked()
        self.flag["shaded_subdivisions"] = self.shade_check.isChecked()

        self.project._recompute_auto_names()
        self.project.mark_dirty()
        self.project.flag_added.emit(self.flag["t"])
        super().accept()

    def _delete_flag(self) -> None:
        """Remove flag and close dialog."""
        if self.flag_idx is not None:
            self.project.remove_flag(self.flag_idx)
        super().accept()

    def _insert_flags_dialog(self) -> None:
        """Ask user how many subdivision flags to insert between two existing ones."""
        left_idx = self.flag_idx
        right_idx = left_idx + 1
        if right_idx >= len(self.project.flags):
            return

        left_flag = self.project.flags[left_idx]
        right_flag = self.project.flags[right_idx]

        max_flags = max(1, int((right_flag["t"] - left_flag["t"]) / 0.1) - 1)

        from PySide6.QtWidgets import QSpinBox, QInputDialog

        count, ok = QInputDialog.getInt(
            self,
            "Insert flags",
            f"How many flags between {left_flag.get('name', 'flag')} and {right_flag.get('name', 'next')}?",
            value=3,
            min=1,
            max=max_flags,
        )
        if ok:
            self.project.insert_equi_spaced_flags(left_idx, right_idx, count)
            super().accept()


class FlagContextMenu:
    """Static helper to open the modal editor."""

    @staticmethod
    def show(
        parent,
        project: Project,
        idx: int,
        global_pos,
        snap_fn: Callable[[float], float] | None = None,
    ) -> None:
        dialog = FlagDialog(parent, project, idx, snap_fn)
        dialog.exec()