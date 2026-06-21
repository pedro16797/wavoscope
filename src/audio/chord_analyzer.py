import numpy as np
import numpy.fft
from typing import Dict, Any

from session.chord_utils import default_chord

def analyze_chord_at(audio_data: np.ndarray, sr: int, t: float, window_s: float = 0.5) -> Dict[str, Any]:
    """
    Suggest a chord based on audio chroma around time t.
    """
    if audio_data is None or len(audio_data) == 0:
        return default_chord()

    # Extract a chunk of audio around t
    start = max(0, int((t - window_s / 2) * sr))
    end = min(len(audio_data), int((t + window_s / 2) * sr))
    chunk = audio_data[start:end]

    if len(chunk) < 1024:
        return default_chord()

    # Compute chroma features manually to avoid librosa/numba build issues
    n_fft = 1 << (len(chunk) - 1).bit_length()
    window = np.hanning(len(chunk))
    spectrum = np.abs(numpy.fft.rfft(chunk * window, n=n_fft))
    freqs = numpy.fft.rfftfreq(n_fft, 1.0 / sr)

    chroma_mean = np.zeros(12)
    # Only consider frequencies from 50Hz to 2000Hz for chord detection.
    mask = (freqs >= 50) & (freqs <= 2000)
    sel_freqs = freqs[mask]
    sel_mags = spectrum[mask]

    if sel_freqs.size:
        # Vectorized chroma accumulation: bin each frequency to a pitch class
        # and sum magnitudes with np.add.at (replaces a per-bin Python loop).
        midi = 69 + 12 * np.log2(sel_freqs / 440.0)
        notes = np.rint(midi).astype(np.int64) % 12
        np.add.at(chroma_mean, notes, sel_mags)

    if np.max(chroma_mean) > 0:
        chroma_mean /= np.max(chroma_mean)

    return analyze_chroma(chroma_mean)


def analyze_chroma(chroma_mean: np.ndarray) -> Dict[str, Any]:
    """
    Suggest a chord based on chroma vector.
    """
    roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Templates: root, major third, fifth
    major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    # Templates: root, minor third, fifth
    minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
    # Templates: root, major third, fifth, minor seventh
    dom7_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
    # Templates: root, minor third, fifth, minor seventh
    m7_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0])
    # Templates: root, major third, fifth, major seventh
    maj7_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1])
    # Templates: root, major third, fifth, sixth
    maj6_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0])
    # Templates: root, second, fifth
    sus2_template = np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0])
    # Templates: root, fourth, fifth
    sus4_template = np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0])
    # Templates: root, minor third, diminished fifth
    dim_template = np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
    # Templates: root, major third, augmented fifth
    aug_template = np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0])

    templates = [
        (major_template, "", ""),
        (minor_template, "m", ""),
        (dom7_template, "", "7"),
        (m7_template, "m", "7"),
        (maj7_template, "", "maj7"),
        (maj6_template, "", "6"),
        (sus2_template, "sus2", ""),
        (sus4_template, "sus4", ""),
        (dim_template, "dim", ""),
        (aug_template, "aug", ""),
    ]

    best_score = -1.0
    best_chord = default_chord()

    for i in range(12):
        for template, quality, extension in templates:
            cur_template = np.roll(template, i)
            # Dot product for similarity
            raw_score = np.dot(chroma_mean, cur_template)

            # Penalise the number of active notes in the template slightly to avoid "over-fitting"
            # simple triads, but normalize by note count so complex chords can still win if they fit well.
            active_notes = np.sum(template)
            score = raw_score / active_notes

            # Small bonus for more complex chords if they match well
            if active_notes > 3:
                score *= 1.05

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
