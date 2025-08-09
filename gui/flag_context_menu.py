from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, 
                               QSpinBox, QCheckBox, QPushButton, QDialogButtonBox)
from PySide6.QtGui import QPalette
from PySide6.QtCore import Qt

class FlagDialog(QDialog):
    def __init__(self, parent, project, idx, snap_fn=None):
        super().__init__(parent)
        self.project = project
        self.flag_idx = idx
        self.flag = project.flags[idx]
        self.snap_fn = snap_fn or (lambda t: round(t * 1000) / 1000)
        
        self.setWindowTitle("Edit Flag")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Remove default styling from labels and checkboxes
        self.setStyleSheet("""
            QLabel {
                border: none;
                padding: 0;
                margin: 0;
            }
            QCheckBox {
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        
        # Name
        label_name = QLabel("Name:")
        label_name.setStyleSheet("border: none; padding: 0; margin: 0;")
        layout.addWidget(label_name)
        
        self.name_edit = QLineEdit(self.flag.get("name", ""))
        self.name_edit.setStyleSheet("border: 1px solid #555; padding: 4px;")
        layout.addWidget(self.name_edit)
        
        # Time
        label_time = QLabel("Time:")
        label_time.setStyleSheet("border: none; padding: 0; margin: 0;")
        layout.addWidget(label_time)
        
        self.time_edit = QDoubleSpinBox()
        self.time_edit.setRange(0, project.duration)
        self.time_edit.setDecimals(3)
        self.time_edit.setValue(self.flag["t"])
        self.time_edit.setStyleSheet("border: 1px solid #555; padding: 2px;")
        layout.addWidget(self.time_edit)
        
        # Subdivision
        label_subdiv = QLabel("Subdivision:")
        label_subdiv.setStyleSheet("border: none; padding: 0; margin: 0;")
        layout.addWidget(label_subdiv)
        
        self.subdiv_edit = QSpinBox()
        self.subdiv_edit.setRange(0, 32)
        self.subdiv_edit.setValue(self.flag.get("subdivision", 0))
        self.subdiv_edit.setStyleSheet("border: 1px solid #555; padding: 2px;")
        layout.addWidget(self.subdiv_edit)
        
        # Checkboxes
        self.section_check = QCheckBox("Section start")
        self.section_check.setChecked(self.flag.get("is_section_start", False))
        self.section_check.setStyleSheet("border: none; padding: 0; margin: 0;")
        layout.addWidget(self.section_check)
        
        self.shade_check = QCheckBox("Shade 8th notes")
        self.shade_check.setChecked(self.flag.get("shaded_subdivisions", False))
        self.shade_check.setStyleSheet("border: none; padding: 0; margin: 0;")
        layout.addWidget(self.shade_check)
        
        # Insert N flags button (only if there's a next flag)
        next_flag_idx = idx + 1
        if next_flag_idx < len(project.flags):
            insert_btn = QPushButton("Insert N flags…")
            insert_btn.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    border: 1px solid #555;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)
            insert_btn.clicked.connect(self.insert_flags)
            layout.addWidget(insert_btn)
        
        layout.addSpacing(8)
        
        # Full-width buttons with matching size and bold text
        buttons_layout = QHBoxLayout()
        
        # Delete button (red)
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                background-color: #ff4444;
                color: white;
                border: 1px solid #555;
                padding: 8px 4px;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        delete_btn.clicked.connect(self.delete_flag)
        buttons_layout.addWidget(delete_btn)

        button_style = """
            QPushButton {
                font-weight: bold;
                border: 1px solid #555;
                padding: 8px 4px;
                min-height: 16px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(button_style)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        # OK button (primary action)
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(button_style)
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        # Make buttons equal width
        buttons_layout.setStretch(0, 1)
        buttons_layout.setStretch(1, 1)
        buttons_layout.setStretch(2, 1)
        
        layout.addLayout(buttons_layout)
    
    def accept(self):
        """Save changes when OK is clicked."""
        self.flag["name"] = self.name_edit.text()
        self.flag["t"] = self.snap_fn(self.time_edit.value())
        self.flag["subdivision"] = self.subdiv_edit.value()
        self.flag["is_section_start"] = self.section_check.isChecked()
        self.flag["shaded_subdivisions"] = self.shade_check.isChecked()
        
        self.project._recompute_auto_names()
        self.project._clear_backend_cache()
        self.project.save()
        self.project.flag_added.emit(self.flag["t"])
        
        super().accept()
    
    def delete_flag(self):
        """Delete the flag."""
        self.project.remove_flag(self.flag_idx)
        super().accept()
    
    def insert_flags(self):
        """Show insert N flags dialog."""
        next_flag_idx = self.flag_idx + 1
        if next_flag_idx >= len(self.project.flags):
            return
            
        left_flag = self.project.flags[self.flag_idx]
        right_flag = self.project.flags
        
        max_flags = int((right_flag["t"] - left_flag["t"]) / 0.1)
        
        count, ok = QSpinBox.getInt(
            self,
            "Insert flags",
            f"Number of flags between {left_flag.get('name', 'flag')} and {right_flag.get('name', 'next')}:",
            value=3,
            minValue=1,
            maxValue=max(1, max_flags - 1),
        )
        
        if ok:
            self.project.insert_equi_spaced_flags(self.flag_idx, next_flag_idx, count)
            super().accept()

class FlagContextMenu:
    @staticmethod
    def show(parent, project, idx, global_pos, snap_fn):
        dialog = FlagDialog(parent, project, idx)
        dialog.exec()