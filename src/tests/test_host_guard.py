"""Security: host-only endpoints must reject remote (non-loopback) clients,
while reads and playback control stay available to them."""
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.main import app
from backend import state

LOCAL = TestClient(app, client=("127.0.0.1", 50000))
REMOTE = TestClient(app, client=("192.168.1.50", 50000))

# A remote client that presents a valid token (a "paired" device).
_TOKEN = "test-remote-token"
REMOTE_AUTH = TestClient(app, client=("192.168.1.50", 50000), headers={"X-Wavoscope-Token": _TOKEN})


def _set_token(value: str) -> None:
    from utils.config import Config
    cfg = Config()
    with cfg._lock:
        if value:
            cfg._data["network.remote_token"] = value
        else:
            cfg._data.pop("network.remote_token", None)


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
    _set_token(_TOKEN)
    try:
        # Even an authorized (tokened) remote gets host paths redacted.
        remote = REMOTE_AUTH.get("/config").json()
        assert remote["autosave_path"] == ""
        assert remote["default_output_folder"] == ""

        local = LOCAL.get("/config").json()
        assert local["autosave_path"] == "/home/alice/secret"
        assert local["default_output_folder"] == "/home/alice/music"
    finally:
        _set_token("")
        with cfg._lock:
            cfg._data.pop("recovery.autosave_path", None)
            cfg._data.pop("ui.default_output_folder", None)


def test_remote_reads_and_playback_require_token():
    # Without a token, a remote client can't read content or drive playback.
    _set_token(_TOKEN)
    try:
        state.project = None
        assert REMOTE.get("/status").status_code == 403

        state.project = MagicMock()
        assert REMOTE.post("/playback", json={"action": "play"}).status_code == 403
    finally:
        state.project = None
        _set_token("")


def test_remote_with_token_allowed_reads_and_playback():
    # A paired remote (valid token) may read and control playback.
    _set_token(_TOKEN)
    try:
        state.project = None
        assert REMOTE_AUTH.get("/status").status_code == 200

        state.project = MagicMock()
        assert REMOTE_AUTH.post("/playback", json={"action": "play"}).status_code == 200
    finally:
        state.project = None
        _set_token("")


def test_remote_rejected_when_no_token_configured():
    # With no token configured at all, remote content access is closed.
    _set_token("")
    state.project = None
    assert REMOTE.get("/status").status_code == 403
    assert REMOTE_AUTH.get("/status").status_code == 403


def test_forged_headers_do_not_grant_host():
    # The guard uses the kernel peer address only: forging Host /
    # X-Forwarded-For / X-Real-IP must not make a remote client look local.
    _set_token("")
    state.project = None
    r = REMOTE.post(
        "/project/open",
        json={"path": "/etc/passwd"},
        headers={"Host": "127.0.0.1", "X-Forwarded-For": "127.0.0.1", "X-Real-IP": "127.0.0.1"},
    )
    assert r.status_code == 403


def test_ipv4_mapped_ipv6_loopback_is_local():
    # ::ffff:127.0.0.1 is loopback and must be treated as the host.
    local6 = TestClient(app, client=("::ffff:127.0.0.1", 50000))
    assert local6.get("/config").status_code == 200


def test_full_127_8_range_is_local():
    # The whole 127.0.0.0/8 block is loopback, not just 127.0.0.1.
    local = TestClient(app, client=("127.0.0.5", 50000))
    assert local.get("/config").status_code == 200


def test_ipv6_loopback_is_local():
    local6 = TestClient(app, client=("::1", 50000))
    assert local6.get("/config").status_code == 200
