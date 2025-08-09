from PySide6.QtWidgets import (QMenu, QInputDialog, QMessageBox)

class FlagContextMenu:
    @staticmethod
    def show(parent, project, idx, global_pos, snap_fn):
        flag = project.flags[idx]
        menu = QMenu(parent)

        rename_action = menu.addAction("Rename…")
        time_action = menu.addAction("Edit Time…")
        subdiv_action = menu.addAction("Subdivision…")
        section_action = menu.addAction("Section start")
        section_action.setCheckable(True)
        section_action.setChecked(flag.get("is_section_start", False))
        
        # NEW: Shading toggle
        shading_action = menu.addAction("Shade 8th notes")
        shading_action.setCheckable(True)
        shading_action.setChecked(flag.get("shaded_subdivisions", False))
        
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
                project.flag_added.emit(flag["t"])

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
                "Sub-beats per measure (0 = inherit):",
                value=flag.get("subdivision", 0),
                minValue=0,
                maxValue=32,
            )
            if ok:
                flag["subdivision"] = new_sub
                project.save()
                project.flag_added.emit(flag["t"])

        elif chosen == delete_action:
            project.remove_flag(idx)

        elif chosen == section_action:
            flag["is_section_start"] = not flag.get("is_section_start", False)
            project.save()
            project.flag_added.emit(flag["t"])

        elif chosen == shading_action:
            flag["shaded_subdivisions"] = not flag.get("shaded_subdivisions", False)
            project.save()
            project.flag_added.emit(flag["t"])