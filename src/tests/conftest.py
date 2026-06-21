"""Shared pytest setup.

``sounddevice`` needs the native PortAudio library, which isn't present in CI.
Register a mock before any test or application module imports it, so the audio
backend's import guards work deterministically regardless of test collection
order. ``setdefault`` leaves a real install (e.g. on a dev machine) untouched,
and individual tests can still override ``sys.modules["sounddevice"]`` as needed.
"""
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("sounddevice", MagicMock())
