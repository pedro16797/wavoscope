"""Atomic JSON persistence shared by the sidecar, playlist, and autosave writers.

Every write goes through :func:`write_json_atomic`, which writes to a temporary
file in the same directory, fsyncs it, then ``os.replace``s it over the target.
``os.replace`` is atomic on POSIX and Windows, so a crash, power loss, or full
disk can never leave a half-written / truncated file — readers always see either
the old content or the complete new content.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from utils.logging import logger


def write_json_atomic(path: Path, data: Any) -> None:
    """Serialize ``data`` to ``path`` atomically. Raises on failure."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False)

    # Temp file in the same directory so os.replace stays on one filesystem.
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
        _fsync_dir(path.parent)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _fsync_dir(directory: Path) -> None:
    """Fsync a directory so the rename from os.replace is itself durable.

    Without this the file contents are on disk but the directory entry pointing
    at them may not be, so a power loss right after os.replace could lose the
    rename. Best-effort: directory fds aren't openable on every platform
    (notably Windows), so failures are ignored.
    """
    try:
        dir_fd = os.open(str(directory), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def read_json(path: Path) -> Any:
    """Read and parse JSON from ``path``. Raises on missing/invalid content."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def quarantine_corrupt_file(path: Path) -> Path | None:
    """Move an unreadable file aside so the next save can't overwrite it.

    Returns the backup path, or ``None`` if it couldn't be moved.
    """
    path = Path(path)
    backup = path.with_suffix(path.suffix + f".corrupt-{int(time.time())}")
    try:
        os.replace(path, backup)
        logger.error(f"Preserved corrupt file {path} as {backup}")
        return backup
    except OSError as e:
        logger.error(f"Could not quarantine corrupt file {path}: {e}")
        return None
