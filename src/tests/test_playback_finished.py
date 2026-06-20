"""A1: playback-finished callbacks run on a worker thread, never on the audio
callback thread — so tearing the stream down from a finished callback is safe."""
import threading

from audio.engine.playback import PlaybackEngine


def test_notify_finished_dispatches_callback():
    eng = PlaybackEngine()
    fired = threading.Event()
    caller = threading.current_thread()
    ran_on = {}

    def cb():
        ran_on["thread"] = threading.current_thread()
        fired.set()

    eng.register_callback("finished", cb)
    eng.notify_finished()

    assert fired.wait(timeout=2.0)
    # Dispatched off the calling (would-be audio) thread.
    assert ran_on["thread"] is not caller
    eng.close()


def test_close_from_within_finished_callback_does_not_deadlock():
    eng = PlaybackEngine()
    done = threading.Event()

    def cb():
        # Mimics the real finished callback, which closes the active project
        # (and thus this engine) from within the dispatch worker.
        eng.close()
        done.set()

    eng.register_callback("finished", cb)
    eng.notify_finished()

    assert done.wait(timeout=2.0)
