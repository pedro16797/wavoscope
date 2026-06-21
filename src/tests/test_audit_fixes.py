"""Regression tests for the post-hardening audit fixes."""
import threading

import numpy as np

from audio.audio_backend import AudioBackend
from audio.waveform_cache import WaveformCache


def test_playlist_mode_finishes_instead_of_looping():
    """C1: in playlist mode the track must reach EOF and fire `finished` (so the
    next item can auto-advance), not loop back to the start forever."""
    be = AudioBackend()
    try:
        sr = be._playback._sr
        be._playback.set_data(np.zeros(sr, dtype=np.float32), sr)  # 1s of audio
        be._playback._playing = True
        be._read_sample_idx = 0
        be._playback._cursor = 0.0

        # Playlist mode enables looping internally but must NOT actually loop.
        be.set_loop_enabled(True)
        be.sync_project_data(flags=[], lyrics=[], loop_mode="playlist",
                             selected_lyric_idx=None, duration=1.0)

        fired = threading.Event()
        be._playback.register_callback("finished", lambda: fired.set())

        frames = 1024
        out = np.zeros((frames, 1), dtype=np.float32)
        for _ in range(sr // frames + 5):
            be._audio_callback(out, frames, None, None)

        assert fired.wait(timeout=2.0), "finished callback never fired in playlist mode"
        assert be._playback._playing is False
    finally:
        be.close()


def test_loop_mode_actually_loops():
    """Counterpart to C1: a real loop mode (whole) must NOT fire `finished`."""
    be = AudioBackend()
    try:
        sr = be._playback._sr
        be._playback.set_data(np.zeros(sr, dtype=np.float32), sr)
        be._playback._playing = True
        be._read_sample_idx = 0
        be._playback._cursor = 0.0

        be.set_loop_enabled(True)
        be.sync_project_data(flags=[], lyrics=[], loop_mode="whole",
                             selected_lyric_idx=None, duration=1.0)

        fired = threading.Event()
        be._playback.register_callback("finished", lambda: fired.set())

        frames = 1024
        out = np.zeros((frames, 1), dtype=np.float32)
        for _ in range(sr // frames + 5):
            be._audio_callback(out, frames, None, None)

        assert not fired.is_set(), "loop mode should not fire finished"
        assert be._playback._playing is True
    finally:
        be.close()


def test_seek_before_loop_clears_range():
    """M5: seeking before the active loop drops the cached range so the new
    position isn't yanked forward."""
    be = AudioBackend()
    try:
        sr = be._playback._sr
        be._playback.set_data(np.zeros(sr * 4, dtype=np.float32), sr)
        be._active_loop_range = (2.0, 3.0)
        be.seek(0.5)  # before loop start
        assert be._active_loop_range is None
    finally:
        be.close()


def test_seek_within_loop_keeps_range():
    be = AudioBackend()
    try:
        sr = be._playback._sr
        be._playback.set_data(np.zeros(sr * 4, dtype=np.float32), sr)
        be._active_loop_range = (2.0, 3.0)
        be.seek(2.5)  # inside the loop
        assert be._active_loop_range == (2.0, 3.0)
    finally:
        be.close()


def test_waveform_bars_count_and_coverage():
    """M4: bars() returns exactly n_bars covering the whole span (no dropped
    final bar, no oversized last bucket)."""
    y = np.linspace(-1.0, 1.0, 101, dtype=np.float32)
    wc = WaveformCache(y, 100)
    for n in (1, 3, 7, 16, 50):
        bars = wc.bars(0.0, 1.0, n)
        assert len(bars) == n, f"expected {n} bars, got {len(bars)}"

    # The final bar must reflect the tail of the signal (max near +1).
    bars = wc.bars(0.0, 1.0, 10)
    _min, _max, _mean, _rms, _intensity = bars[-1]
    assert _max > 0.8


def test_waveform_more_bars_than_samples_is_clamped():
    y = np.array([0.0, 0.5, -0.5], dtype=np.float32)
    wc = WaveformCache(y, 3)
    bars = wc.bars(0.0, 1.0, 100)
    # Can't have more buckets than samples.
    assert len(bars) <= 3
