import { describe, it, expect } from 'vitest';
import { formatChord, getChordMidiNotes, midiToFreq, type Chord } from './useStore';

describe('Store Utilities', () => {
  it('formats chords correctly', () => {
    const chord: Chord = {
      root: 'C',
      accidental: '#',
      quality: 'm',
      extension: '7',
      alterations: ['b5'],
      additions: ['add9'],
      bass: 'G',
      bass_accidental: ''
    };
    // C#m7b5add9/G
    expect(formatChord(chord)).toBe('C#m7b5add9/G');
  });

  it('calculates frequency from midi', () => {
    expect(midiToFreq(69)).toBe(440);
    expect(midiToFreq(60)).toBeCloseTo(261.63, 2);
  });

  it('gets correct midi notes for a major chord', () => {
    const chord: Chord = {
      root: 'C',
      accidental: '',
      quality: 'M',
      extension: '',
      alterations: [],
      additions: [],
      bass: '',
      bass_accidental: ''
    };
    const notes = getChordMidiNotes(chord);
    // C4(60), E4(64), G4(67) + Bass C3(48)
    expect(notes).toContain(60);
    expect(notes).toContain(64);
    expect(notes).toContain(67);
    expect(notes).toContain(48);
  });
});
