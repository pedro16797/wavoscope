import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock sounddevice
mock_sd = MagicMock()
sys.modules["sounddevice"] = mock_sd

from audio.audio_backend import AudioBackend

def test_list_devices():
    mock_sd.query_devices.return_value = [
        {'name': 'Device 1', 'max_output_channels': 2, 'hostapi': 0},
        {'name': 'Device 2', 'max_output_channels': 0, 'hostapi': 0},
        {'name': 'Device 3', 'max_output_channels': 1, 'hostapi': 1},
    ]
    mock_sd.default.device = (0, 0)

    devices = AudioBackend.list_devices()
    assert len(devices) == 2
    assert devices[0]['name'] == 'Device 1'
    assert devices[0]['is_default'] is True
    assert devices[1]['name'] == 'Device 3'
    assert devices[1]['is_default'] is False

def test_set_device():
    backend = AudioBackend()
    mock_sd.query_devices.return_value = [
        {'name': 'Device 1', 'max_output_channels': 2, 'hostapi': 0},
        {'name': 'Device 3', 'max_output_channels': 1, 'hostapi': 1},
    ]

    backend.set_device('Device 3')
    assert backend._selected_device_name == 'Device 3'
    assert backend._playback._device == 1
    assert backend._synth._device == 1

def test_set_device_default():
    backend = AudioBackend()
    backend.set_device(None)
    assert backend._selected_device_name is None
    assert backend._playback._device is None
    assert backend._synth._device is None
