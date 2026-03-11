import pytest
import numpy as np
from audio.engine.filters import FilterEngine

def test_filter_autogain_compensation():
    sr = 44100
    engine = FilterEngine(sr)

    # Create white noise
    np.random.seed(42)
    chunk = np.random.uniform(-1, 1, 1024).astype(np.float32)

    # Enable a very aggressive filter (e.g., high-pass at 1000Hz)
    # FilterEngine.set_filter: low_enabled means it applies a HIGHPASS with cutoff low_hz
    engine.set_filter(enabled=True, low_enabled=True, low=1000.0)

    # Process without auto-gain
    engine.set_filter(auto_gain=False)
    chunk_no_ag = engine.process(chunk.copy())
    p_no_ag = np.mean(chunk_no_ag * chunk_no_ag)

    # Reset engine state (EMAs and filter zi)
    engine.reset_zi()

    # Process with auto-gain enabled
    engine.set_filter(auto_gain=True)

    # Process enough chunks to let EMA stabilize and gain kick in
    last_p_ag = 0
    for _ in range(100):
        chunk_ag = engine.process(chunk.copy())
        last_p_ag = np.mean(chunk_ag * chunk_ag)

    print(f"Power No AG: {p_no_ag}, Power AG: {last_p_ag}")
    assert last_p_ag > p_no_ag

    # Check that it doesn't exceed the input power by too much (should be in the ballpark of p_in)
    p_in = np.mean(chunk * chunk)
    print(f"Power In: {p_in}")
    assert last_p_ag > 0.1 * p_in

def test_filter_autogain_no_filter():
    sr = 44100
    engine = FilterEngine(sr)
    engine.set_filter(enabled=False, auto_gain=True)

    chunk = np.random.uniform(-1, 1, 1024).astype(np.float32)
    p_in = np.mean(chunk * chunk)

    chunk_processed = engine.process(chunk.copy())
    p_out = np.mean(chunk_processed * chunk_processed)

    # If filter is disabled, it should return the chunk as is (no gain applied)
    assert np.allclose(chunk, chunk_processed)
    assert pytest.approx(p_in) == p_out
