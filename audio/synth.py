import numpy as np
import sounddevice as sd

class SimpleSynth:
    """
    Generates simple sine waves on demand for piano keys.
    """
    def __init__(self, sr=44100):
        self.sr = sr
        self._active = {}
        self._stream = sd.OutputStream(
            samplerate=self.sr, channels=1,
            callback=self._callback
        )
        self._stream.start()

    def stop_all(self):
        self._active.clear()

    def start_tone(self, freq):
        self._active[freq] = 0.0  # phase

    def stop_tone(self, freq):
        self._active.pop(freq, None)

    def _callback(self, outdata, frames, time, status):
        t = np.arange(frames) / self.sr
        out = np.zeros(frames)
        for freq, phase in list(self._active.items()):
            wave = 0.2 * np.sin(2 * np.pi * freq * (t + phase))
            out += wave
            self._active[freq] = phase + frames / self.sr
        out *= 0.8 / max(1, len(self._active))
        outdata[:, 0] = out