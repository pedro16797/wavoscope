import threading
import time
import tempfile
from pathlib import Path
from backend import state
from utils.config import Config
from utils.logging import logger

class AutosaveManager:
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("AutosaveManager started")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            logger.info("AutosaveManager stopped")

    def _run(self):
        last_save_time = 0
        while not self._stop_event.is_set():
            try:
                cfg = Config()
                enabled = cfg.get("recovery.autosave_enabled", True)
                forced = cfg.get("recovery.autosave_forced", False)
                interval_min = cfg.get("recovery.autosave_interval_minutes", 5)
                interval_sec = interval_min * 60

                now = time.time()

                if enabled and state.project:
                    if forced or state.project._dirty:
                        if now - last_save_time >= interval_sec:
                            self._do_autosave()
                            last_save_time = time.time()

                # Sleep in small increments to respond quickly to stop event
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in autosave loop: {e}")
                time.sleep(10)

    def _do_autosave(self):
        cfg = Config()
        max_snapshots = cfg.get("recovery.autosave_max_snapshots", 5)
        path_str = cfg.get("recovery.autosave_path", "")

        if not path_str:
            autosave_dir = Path(tempfile.gettempdir()) / "wavoscope_autosaves"
        else:
            autosave_dir = Path(path_str)

        try:
            autosave_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create autosave directory {autosave_dir}: {e}")
            return

        if not state.project:
            return

        original_stem = state.project.audio_path.stem

        # Rotate existing snapshots
        for i in range(max_snapshots - 1, 0, -1):
            old_file = autosave_dir / f"{original_stem}.autosave.{i}.oscope"
            new_file = autosave_dir / f"{original_stem}.autosave.{i+1}.oscope"
            if old_file.exists():
                try:
                    if i + 1 > max_snapshots:
                        old_file.unlink()
                    else:
                        if new_file.exists():
                            new_file.unlink()
                        old_file.rename(new_file)
                except Exception as e:
                    logger.error(f"Error rotating autosave {old_file}: {e}")

        # Save new snapshot as .1.oscope
        target = autosave_dir / f"{original_stem}.autosave.1.oscope"
        try:
            state.project._manager.save(target)
            logger.info(f"Autosave created: {target}")
        except Exception as e:
            logger.error(f"Autosave failed to save {target}: {e}")

# Global instance
_manager = AutosaveManager()

def start():
    _manager.start()

def stop():
    _manager.stop()
