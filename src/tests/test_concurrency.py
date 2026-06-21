"""B1/B3: atomic project swaps and thread-safe Config."""
import threading
from unittest.mock import MagicMock

from backend import state
from utils import config as config_mod
from utils.config import Config


def test_set_project_swaps_and_closes_previous():
    state.project = None
    a, b = MagicMock(), MagicMock()

    state.set_project(a)
    assert state.project is a
    a.close.assert_not_called()

    state.set_project(b)
    assert state.project is b
    a.close.assert_called_once()      # previous project closed exactly once
    b.close.assert_not_called()

    state.set_project(None)
    assert state.project is None
    b.close.assert_called_once()


def test_config_missing_key_returns_default(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "_CONFIG_PATH", tmp_path / "cfg.json")
    Config._instance = None
    try:
        cfg = Config()
        assert cfg.get("does.not.exist", "fallback") == "fallback"
        # A real default from default.json still resolves.
        assert isinstance(cfg.get("ui.theme"), str)
    finally:
        Config._instance = None  # let other tests rebuild from the real path


def test_config_get_returns_dict_subtree(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "_CONFIG_PATH", tmp_path / "cfg.json")
    Config._instance = None
    try:
        cfg = Config()
        # ui.keybinds is a plain dict (no "default" wrapper) in default.json;
        # get() must return the subtree, not the caller's fallback.
        keybinds = cfg.get("ui.keybinds", "FALLBACK")
        assert isinstance(keybinds, dict) and keybinds
    finally:
        Config._instance = None


def test_config_set_is_atomic_and_thread_safe(tmp_path, monkeypatch):
    cfg_path = tmp_path / "cfg.json"
    monkeypatch.setattr(config_mod, "_CONFIG_PATH", cfg_path)
    Config._instance = None
    try:
        cfg = Config()
        cfg.set("ui.theme", "neon")
        assert cfg.get("ui.theme") == "neon"
        assert cfg_path.exists()

        errors = []

        def worker():
            try:
                for i in range(200):
                    cfg.set(f"k{i % 5}", i)
                    cfg.get(f"k{i % 5}")
            except Exception as e:  # e.g. "dict changed size during iteration"
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors

        # The on-disk file must reflect the latest write (no stale/torn snapshot).
        from utils.persistence import read_json
        cfg.set("final", "value")
        assert read_json(cfg_path)["final"] == "value"
        assert cfg.get("final") == "value"
    finally:
        Config._instance = None
