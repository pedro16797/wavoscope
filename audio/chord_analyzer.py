import numpy as np
import librosa
from typing import Dict, Any

def analyze_chord_at(y: np.ndarray, sr: int, t: float, window_s: float = 0.5) -> Dict[str, Any]:
    """
    Suggest a chord based on audio chroma around time t.
    """
    if y is None or len(y) == 0:
        return _default_chord()

    # Extract a chunk of audio around t
    start = max(0, int((t - window_s / 2) * sr))
    end = min(len(y), int((t + window_s / 2) * sr))
    chunk = y[start:end]

    if len(chunk) < 1024:
        return _default_chord()

    # Compute chroma features
    # Use CENS for better robustness to dynamics
    chroma = librosa.feature.chroma_cens(y=chunk, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

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
        (major_template, "M", ""),
        (minor_template, "m", ""),
        (dom7_template, "M", "7"),
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
                    "root": root_name[0],
                    "accidental": root_name[1:] if len(root_name) > 1 else "",
                    "quality": quality,
                    "extension": extension,
                    "alterations": [],
                    "additions": [],
                    "bass": "",
                    "bass_accidental": "",
                }

    return best_chord

def _default_chord() -> Dict[str, Any]:
    return {
        "root": "C",
        "accidental": "",
        "quality": "M",
        "extension": "",
        "alterations": [],
        "additions": [],
        "bass": "",
        "bass_accidental": "",
    }
