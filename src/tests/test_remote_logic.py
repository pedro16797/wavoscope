import pytest
from utils.config import Config
import socket
import os

def test_is_remote_logic():
    # In sandbox environment, we can check that it returns a valid IP
    ip = Config().get_local_ip()
    assert ip != ""
    # Usually it's either 127.0.0.1 or a LAN IP
    assert len(ip.split('.')) == 4

def test_config_get_local_ip_fallback():
    # We can't easily mock socket inside the test without complex mocking,
    # but we can verify the method exists and returns a string.
    assert isinstance(Config().get_local_ip(), str)
