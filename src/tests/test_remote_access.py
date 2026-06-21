import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import state

client = TestClient(app, client=("127.0.0.1", 50000))

def test_get_remote_url():
    state.port = 1234
    response = client.get("/config/remote-url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    # May be ":1234" or ":1234/?token=..." depending on whether a token exists.
    assert ":1234" in data["url"]
    assert data["url"].startswith("http://")

def test_config_remote_access():
    # Test getting config
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "remote_access" in data

    # Test updating config
    response = client.post("/config", json={"remote_access": True})
    assert response.status_code == 200

    response = client.get("/config")
    assert response.status_code == 200
    assert response.json()["remote_access"] is True

    # Enabling remote access mints a token; verify and then clean both up.
    from utils.config import Config
    assert Config().get("network.remote_token", "")

    client.post("/config", json={"remote_access": False})
    cfg = Config()
    with cfg._lock:
        cfg._data.pop("network.remote_token", None)
