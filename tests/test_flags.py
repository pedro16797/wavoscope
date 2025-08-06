import pytest
import numpy as np
import soundfile as sf
from wavoscope.session.project import Project

@pytest.fixture
def proj(tmp_path):
    wav_path = tmp_path / "test.wav"
    sr = 44100
    silence = np.zeros(sr, dtype='float32')
    sf.write(str(wav_path), silence, sr)
    p = Project(wav_path)
    p.open_file(wav_path)
    return p