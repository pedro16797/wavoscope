"""Data safety: atomic writes, schema versioning, and corrupt-file recovery."""
import json

from session.manager import ProjectManager, SCHEMA_VERSION
from utils.persistence import write_json_atomic, read_json


def test_atomic_write_roundtrip(tmp_path):
    p = tmp_path / "data.json"
    write_json_atomic(p, {"a": 1, "b": [1, 2, 3]})
    assert read_json(p) == {"a": 1, "b": [1, 2, 3]}
    # No temp files left behind.
    assert list(tmp_path.glob(".*.tmp")) == []


def test_save_writes_version(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"x")
    mgr = ProjectManager(audio)
    mgr.save()
    data = json.loads(mgr.sidecar_path.read_text(encoding="utf-8"))
    assert data["version"] == SCHEMA_VERSION


def test_round_trip_preserves_content(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"x")
    mgr = ProjectManager(audio)
    mgr.session_data["flags"] = [
        {"t": 1.5, "type": "rhythm", "div": 4, "n": "", "s": False, "divshade": False}
    ]
    mgr.save()

    reloaded = ProjectManager(audio)
    assert reloaded.session_data["flags"][0]["t"] == 1.5
    assert reloaded.session_data["flags"][0]["div"] == 4


def test_corrupt_sidecar_is_quarantined_not_discarded(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"x")
    sidecar = audio.with_suffix(audio.suffix + ".oscope")
    sidecar.write_text("{ not valid json", encoding="utf-8")

    mgr = ProjectManager(audio)  # load() should quarantine, not overwrite

    # A fresh, usable session is loaded.
    assert mgr.session_data["flags"] == []
    # The corrupt bytes are preserved for recovery rather than destroyed.
    backups = list(tmp_path.glob("song.wav.oscope.corrupt-*"))
    assert len(backups) == 1
    assert "not valid json" in backups[0].read_text(encoding="utf-8")
    # The original path was moved aside (a clean save can now take its place).
    assert not sidecar.exists()


def test_newer_version_loads_best_effort(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"x")
    sidecar = audio.with_suffix(audio.suffix + ".oscope")
    sidecar.write_text(
        json.dumps({"version": SCHEMA_VERSION + 99, "flags": [{"t": 2.0}]}),
        encoding="utf-8",
    )

    mgr = ProjectManager(audio)
    # Still loads the data rather than discarding it.
    assert mgr.session_data["flags"][0]["t"] == 2.0
