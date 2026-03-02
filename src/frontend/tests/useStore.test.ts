import { describe, it, expect } from 'vitest';
import { formatChord, getChordMidiNotes, midiToFreq, getTimelineStep, formatTimelineLabel } from '../src/store/utils';
import type { Chord } from '../src/store/types';

describe('Store Utilities', () => {
  it('formats chords correctly', () => {
    const chord: Chord = {
      r: 'C',
      ca: '#',
      q: 'm',
      ext: '7',
      alt: ['b5'],
      add: ['add9'],
      b: 'G',
      ba: ''
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
      r: 'C',
      ca: '',
      q: '',
      ext: '',
      alt: [],
      add: [],
      b: '',
      ba: ''
    };
    const notes = getChordMidiNotes(chord);
    // C4(60), E4(64), G4(67) + Bass C3(48)
    expect(notes).toContain(60);
    expect(notes).toContain(64);
    expect(notes).toContain(67);
    expect(notes).toContain(48);
  });

  describe('Timeline Utilities', () => {
    it('calculates correct timeline steps', () => {
      // < 30s region (1-5-10 pattern)
      expect(getTimelineStep(0.1)).toBe(0.01);
      expect(getTimelineStep(0.4)).toBe(0.05);
      expect(getTimelineStep(1)).toBe(0.1);
      expect(getTimelineStep(4)).toBe(0.5);
      expect(getTimelineStep(10)).toBe(1);
      expect(getTimelineStep(40)).toBe(5);
      expect(getTimelineStep(100)).toBe(10);

      // 30s to 30min region
      expect(getTimelineStep(200)).toBe(30);
      expect(getTimelineStep(400)).toBe(60);
      expect(getTimelineStep(2000)).toBe(300);
      expect(getTimelineStep(4000)).toBe(600);
      expect(getTimelineStep(10000)).toBe(1800);

      // > 30min region (1-5-10 hours pattern)
      expect(getTimelineStep(20000)).toBe(3600);    // ~1h
      expect(getTimelineStep(100000)).toBe(18000);  // ~5h
      expect(getTimelineStep(200000)).toBe(36000);  // ~10h
      expect(getTimelineStep(1000000)).toBe(180000); // ~50h
    });

    it('formats timeline labels correctly', () => {
      expect(formatTimelineLabel(65, 1)).toBe('1:05');
      expect(formatTimelineLabel(3661, 1)).toBe('1:01:01');
      expect(formatTimelineLabel(1.5, 0.1)).toBe('0:01.5');
      expect(formatTimelineLabel(1.5, 0.01)).toBe('0:01.50');
      expect(formatTimelineLabel(3600.5, 0.1)).toBe('1:00:00.5');
    });
  });
});
