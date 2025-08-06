from PySide6.QtWidgets import (QMenu, QInputDialog, QMessageBox)

class FlagContextMenu:
    @staticmethod
    def show(parent, project, idx, global_pos, snap_fn):
        flag = project.flags[idx]
        menu = QMenu(parent)

        rename_action = menu.addAction("Rename…")
        time_action = menu.addAction("Edit Time…")
        subdiv_action = menu.addAction("Subdivision…")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")

        chosen = menu.exec(global_pos)
        if chosen is None:
            return

        if chosen == rename_action:
            new_name, ok = QInputDialog.getText(
                parent, "Rename flag", "New name:", text=flag.get("name", "")
            )
            if ok:
                flag["name"] = new_name
                project.save()
                project.flag_added.emit(flag["t"])  # re-render

        elif chosen == time_action:
            new_time, ok = QInputDialog.getDouble(
                parent,
                "Edit timestamp",
                "Time (sec):",
                value=flag["t"],
                decimals=3,
                minValue=0.0,
                maxValue=project.duration,
            )
            if ok:
                new_time = snap_fn(new_time)
                project.move_flag(idx, new_time)

        elif chosen == subdiv_action:
            new_sub, ok = QInputDialog.getInt(
                parent,
                "Set subdivision",
                "Sub-beats per measure:",
                value=flag.get("subdivision", 1),
                minValue=1,
                maxValue=32,
            )
            if ok:
                flag["subdivision"] = new_sub
                project.save()
                project.flag_added.emit(flag["t"])

        elif chosen == delete_action:
            reply = QMessageBox.question(
                parent,
                "Delete flag?",
                f'Delete {flag["type"]} flag at {flag["t"]:.2f}s?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                project.remove_flag(idx)