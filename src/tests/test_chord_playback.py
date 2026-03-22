
import unittest
from session.chord_utils import get_chord_midi_notes

class TestChordUtils(unittest.TestCase):
    def test_basic_major(self):
        # C Major: C4, E4, G4 (60, 64, 67) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': '', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 64, 67])

    def test_inversion_c_over_e(self):
        # C/E: C4, E4, G4 (60, 64, 67) + Bass E2 (40)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': '', 'alt': [], 'add': [], 'b': 'E', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [40, 60, 64, 67])

    def test_inversion_c_over_g(self):
        # C/G: C4, E4, G4 (60, 64, 67) + Bass G2 (43)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': '', 'alt': [], 'add': [], 'b': 'G', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [43, 60, 64, 67])

    def test_maj7(self):
        # Cmaj7: C4, E4, G4, B4 (60, 64, 67, 71) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': 'maj7', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertIn(71, notes)
        self.assertIn(36, notes)

    def test_msus4(self):
        # Cmsus4: C4, Eb4, F4, G4 (60, 63, 65, 67) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': 'msus4', 'ext': '', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 63, 65, 67])

    def test_octave_shift_g(self):
        # G Major: G3, B3, D4 (55, 59, 62) + Bass G2 (43)
        chord = {'r': 'G', 'ca': '', 'q': '', 'ext': '', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [43, 55, 59, 62])

    def test_msus2(self):
        # Cmsus2: C4, D4, Eb4, G4 (60, 62, 63, 67) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': 'msus2', 'ext': '', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 62, 63, 67])

    def test_c_6(self):
        # C6: C4, E4, G4, A4 (60, 64, 67, 69) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': '6', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 64, 67, 69])

    def test_maj9(self):
        # Cmaj9: C4, E4, G4, B4, D5 (60, 64, 67, 71, 74) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': 'maj9', 'alt': [], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 64, 67, 71, 74])

    def test_m7b5(self):
        # Cm7b5: C4, Eb4, Gb4, Bb4 (60, 63, 66, 70) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': 'm', 'ext': '7', 'alt': ['b5'], 'add': [], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 63, 66, 70])

    def test_add2_add4(self):
        # Cadd2add4: C4, D4, E4, F4, G4 (60, 62, 64, 65, 67) + Bass C2 (36)
        chord = {'r': 'C', 'ca': '', 'q': '', 'ext': '', 'alt': [], 'add': ['add2', 'add4'], 'b': '', 'ba': ''}
        notes = get_chord_midi_notes(chord)
        self.assertEqual(notes, [36, 60, 62, 64, 65, 67])

if __name__ == '__main__':
    unittest.main()
