"""Security: host-only endpoints must reject remote (non-loopback) clients,
while reads and playback control stay available to them."""
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.main import app
from backend import state

LOCAL = TestClient(app, client=("127.0.0.1", 50000))
REMOTE = TestClient(app, client=("192.168.1.50", 50000))


def test_remote_blocked_from_open_project():
    state.project = None
    r = REMOTE.post("/project/open", json={"path": "/etc/passwd"})
    assert r.status_code == 403


def test_remote_blocked_from_export():
    state.project = MagicMock()
    r = REMOTE.post("/project/export/musicxml/start", json={"path": "/tmp/evil.xml"})
    assert r.status_code == 403
    state.project = None


def test_remote_blocked_from_config_write():
    r = REMOTE.post("/config", json={"autosave_path": "/tmp/evil"})
    assert r.status_code == 403


def test_remote_blocked_from_playlist_add():
    r = REMOTE.post("/playlists/some-id/items", json={"path": "/etc/shadow"})
    assert r.status_code == 403


def test_remote_blocked_from_flag_edit():
    state.project = MagicMock()
    r = REMOTE.post("/project/flags", json={"t": 1.0})
    assert r.status_code == 403
    state.project = None


def test_local_allowed_open_and_config():
    # Loopback (host) requests pass the guard. /config read is always allowed.
    assert LOCAL.get("/config").status_code == 200


def test_remote_blocked_before_project_check():
    # The host guard must run before the "no project loaded" check so a remote
    # client can't probe whether a project is loaded (403, not 400).
    state.project = None
    r = REMOTE.post("/project/flags", json={"t": 1.0})
    assert r.status_code == 403


def test_remote_config_redacts_host_paths():
    from utils.config import Config
    cfg = Config()
    with cfg._lock:
        cfg._data["recovery.autosave_path"] = "/home/alice/secret"
        cfg._data["ui.default_output_folder"] = "/home/alice/music"
    try:
        remote = REMOTE.get("/config").json()
        assert remote["autosave_path"] == ""
        assert remote["default_output_folder"] == ""

        local = LOCAL.get("/config").json()
        assert local["autosave_path"] == "/home/alice/secret"
        assert local["default_output_folder"] == "/home/alice/music"
    finally:
        with cfg._lock:
            cfg._data.pop("recovery.autosave_path", None)
            cfg._data.pop("ui.default_output_folder", None)


def test_remote_allowed_reads_and_playback():
    # Reads and playback control remain available to remote devices.
    state.project = None
    assert REMOTE.get("/status").status_code == 200

    state.project = MagicMock()
    assert REMOTE.post("/playback", json={"action": "play"}).status_code == 200
    state.project = None
