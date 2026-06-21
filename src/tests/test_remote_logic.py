import ipaddress
from types import SimpleNamespace

from utils.config import Config


def test_get_local_ip_is_a_valid_address():
    ip = Config().get_local_ip()
    # Must be a parseable IPv4/IPv6 address, not just any non-empty string.
    ipaddress.ip_address(ip)


def _fake_request(host: str, headers=None, query=None):
    return SimpleNamespace(
        client=SimpleNamespace(host=host),
        headers=headers or {},
        query_params=query or {},
    )


def test_is_local_request_covers_loopback_forms():
    from backend.deps import is_local_request
    for host in ("127.0.0.1", "127.0.0.5", "::1", "::ffff:127.0.0.1", "localhost"):
        assert is_local_request(_fake_request(host)), host
    for host in ("192.168.1.10", "10.0.0.1", "8.8.8.8"):
        assert not is_local_request(_fake_request(host)), host


def test_is_authorized_request_token_logic():
    from backend.deps import is_authorized_request
    cfg = Config()
    with cfg._lock:
        cfg._data["network.remote_token"] = "sekret"
    try:
        # Local is always authorized, token or not.
        assert is_authorized_request(_fake_request("127.0.0.1"))
        # Remote needs the exact token (header or query).
        assert not is_authorized_request(_fake_request("192.168.1.10"))
        assert not is_authorized_request(_fake_request("192.168.1.10", headers={"x-wavoscope-token": "wrong"}))
        assert is_authorized_request(_fake_request("192.168.1.10", headers={"x-wavoscope-token": "sekret"}))
        assert is_authorized_request(_fake_request("192.168.1.10", query={"token": "sekret"}))
    finally:
        with cfg._lock:
            cfg._data.pop("network.remote_token", None)

    # With no token configured, remote is closed even if one is presented.
    assert not is_authorized_request(_fake_request("192.168.1.10", headers={"x-wavoscope-token": "sekret"}))
