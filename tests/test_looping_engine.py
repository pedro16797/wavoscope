import pytest
from session.looping import LoopingEngine

def test_looping_engine_before_first_region():
    engine = LoopingEngine()
    duration = 100.0
    flags = [
        {"t": 10.0, "type": "rhythm", "div": 4},
        {"t": 20.0, "type": "rhythm", "div": 4},
        {"t": 30.0, "type": "rhythm", "div": 4, "s": True},
        {"t": 40.0, "type": "rhythm", "div": 4, "s": True},
    ]
    lyrics = [
        {"t": 50.0, "l": 5.0, "s": "test"}
    ]

    # Test Bar mode before first flag
    engine.set_loop_mode("bar")
    # Current behavior: should loop the first bar (10.0 to 20.0) if playhead is at 5.0
    assert engine.get_loop_range(5.0, duration, flags) == (10.0, 20.0)
    # Inside first bar
    assert engine.get_loop_range(15.0, duration, flags) == (10.0, 20.0)
    # After last flag
    assert engine.get_loop_range(45.0, duration, flags) == (40.0, duration)

    # Test Section mode before first section
    engine.set_loop_mode("section")
    # First section starts at 30.0
    assert engine.get_loop_range(5.0, duration, flags) == (30.0, 40.0)
    # After last section
    assert engine.get_loop_range(45.0, duration, flags) == (40.0, duration)

    # Test Lyric mode before first lyric
    engine.set_loop_mode("lyric")
    assert engine.get_loop_range(5.0, duration, flags, lyrics) == (50.0, 55.0)

def test_looping_engine_whole():
    engine = LoopingEngine()
    engine.set_loop_mode("whole")
    assert engine.get_loop_range(50.0, 100.0, []) == (0.0, 100.0)

def test_looping_engine_none():
    engine = LoopingEngine()
    engine.set_loop_mode("none")
    assert engine.get_loop_range(50.0, 100.0, []) == (0.0, 100.0)
