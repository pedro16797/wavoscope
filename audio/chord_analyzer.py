import numpy as np
import numpy.fft
from typing import Dict, Any

def analyze_chord_at(audio_data: np.ndarray, sr: int, t: float, window_s: float = 0.5) -> Dict[str, Any]:
    """
    Suggest a chord based on audio chroma around time t.
    """
    if audio_data is None or len(audio_data) == 0:
        return _default_chord()

    # Extract a chunk of audio around t
    start = max(0, int((t - window_s / 2) * sr))
    end = min(len(audio_data), int((t + window_s / 2) * sr))
    chunk = audio_data[start:end]

    if len(chunk) < 1024:
        return _default_chord()

    # Compute chroma features manually to avoid librosa/numba build issues
    n_fft = 1 << (len(chunk) - 1).bit_length()
    window = np.hanning(len(chunk))
    spectrum = np.abs(numpy.fft.rfft(chunk * window, n=n_fft))
    freqs = numpy.fft.rfftfreq(n_fft, 1.0 / sr)

    chroma_mean = np.zeros(12)
    # Only consider frequencies from 50Hz to 2000Hz for chord detection
    mask = (freqs >= 50) & (freqs <= 2000)

    for f, mag in zip(freqs[mask], spectrum[mask]):
        if f <= 0:
            continue
        # MIDI note: 69 + 12 * log2(f / 440)
        midi = 69 + 12 * np.log2(f / 440.0)
        note = int(round(midi)) % 12
        chroma_mean[note] += mag

    if np.sum(chroma_mean) > 0:
        chroma_mean /= np.max(chroma_mean)

    roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Templates: root, major third, fifth
    major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    # Templates: root, minor third, fifth
    minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
    # Templates: root, major third, fifth, minor seventh
    dom7_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
    # Templates: root, minor third, fifth, minor seventh
    m7_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0])

    templates = [
        (major_template, "", ""),
        (minor_template, "m", ""),
        (dom7_template, "", "7"),
        (m7_template, "m", "7"),
    ]

    best_score = -1.0
    best_chord = _default_chord()

    for i in range(12):
        for template, quality, extension in templates:
            cur_template = np.roll(template, i)
            # Dot product for similarity
            score = np.dot(chroma_mean, cur_template)

            if score > best_score:
                best_score = score
                root_name = roots[i]
                best_chord = {
                    "r": root_name[0],
                    "ca": root_name[1:] if len(root_name) > 1 else "",
                    "q": quality,
                    "ext": extension,
                    "alt": [],
                    "add": [],
                    "b": "",
                    "ba": "",
                }

    return best_chord

def _default_chord() -> Dict[str, Any]:
    return {
        "r": "C",
        "ca": "",
        "q": "",
        "ext": "",
        "alt": [],
        "add": [],
        "b": "",
        "ba": "",
    }
