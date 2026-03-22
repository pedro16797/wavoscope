
import unittest
import numpy as np
from audio.chord_analyzer import analyze_chroma

class TestChordAnalyzer(unittest.TestCase):
    def test_major_detection(self):
        # C Major: C, E, G (indices 0, 4, 7)
        chroma = np.zeros(12)
        chroma[[0, 4, 7]] = 1.0
        res = analyze_chroma(chroma)
        self.assertEqual(res['r'], 'C')
        self.assertEqual(res['q'], '')
        self.assertEqual(res['ext'], '')

    def test_minor_detection(self):
        # C Minor: C, Eb, G (indices 0, 3, 7)
        chroma = np.zeros(12)
        chroma[[0, 3, 7]] = 1.0
        res = analyze_chroma(chroma)
        self.assertEqual(res['r'], 'C')
        self.assertEqual(res['q'], 'm')
        self.assertEqual(res['ext'], '')

    def test_maj7_detection(self):
        # Cmaj7: C, E, G, B (indices 0, 4, 7, 11)
        chroma = np.zeros(12)
        chroma[[0, 4, 7, 11]] = 1.0
        res = analyze_chroma(chroma)
        self.assertEqual(res['r'], 'C')
        self.assertEqual(res['q'], '')
        self.assertEqual(res['ext'], 'maj7')

    def test_dom7_detection(self):
        # C7: C, E, G, Bb (indices 0, 4, 7, 10)
        chroma = np.zeros(12)
        chroma[[0, 4, 7, 10]] = 1.0
        res = analyze_chroma(chroma)
        self.assertEqual(res['r'], 'C')
        self.assertEqual(res['q'], '')
        self.assertEqual(res['ext'], '7')

    def test_sus4_detection(self):
        # Csus4: C, F, G (indices 0, 5, 7)
        chroma = np.zeros(12)
        chroma[[0, 5, 7]] = 1.0
        res = analyze_chroma(chroma)
        self.assertEqual(res['r'], 'C')
        self.assertEqual(res['q'], 'sus4')

if __name__ == '__main__':
    unittest.main()
