import type { Chord } from './types';

export const midiToFreq = (midi: number) => 440.0 * Math.pow(2, (midi - 69) / 12);
export const freqToMidi = (freq: number) => 12 * Math.log2(freq / 440) + 69;

export const formatChord = (chord: Chord): string => {
  let s = chord.root + chord.accidental;
  if (chord.quality !== 'M') s += chord.quality;
  s += chord.extension;
  chord.alterations.forEach(a => s += a);
  chord.additions.forEach(a => s += a);
  if (chord.bass) s += '/' + chord.bass + chord.bass_accidental;
  return s;
};

export const getChordMidiNotes = (chord: Chord): number[] => {
  const rootMap: Record<string, number> = { 'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11 };
  const root = (rootMap[chord.root] || 0) + (chord.accidental === '#' ? 1 : chord.accidental === 'b' ? -1 : 0);
  const base = 60 + root; // C4 base

  const intervals: number[] = [0]; // Intervals relative to root

  // Quality
  if (chord.quality === 'm') intervals.push(3, 7);
  else if (chord.quality === 'dim') intervals.push(3, 6);
  else if (chord.quality === 'aug') intervals.push(4, 8);
  else if (chord.quality === 'sus2') intervals.push(2, 7);
  else if (chord.quality === 'sus4') intervals.push(5, 7);
  else intervals.push(4, 7); // Default to Major

  // Extension
  if (chord.extension === '7') {
    if (chord.quality === 'dim') intervals.push(9); // Full dim
    else intervals.push(10); // dominant/minor 7th
  } else if (chord.extension === '9') {
    intervals.push(chord.quality === 'dim' ? 9 : 10, 14);
  } else if (chord.extension === '11') {
    intervals.push(chord.quality === 'dim' ? 9 : 10, 14, 17);
  } else if (chord.extension === '13') {
    intervals.push(chord.quality === 'dim' ? 9 : 10, 14, 17, 21);
  }

  // Alterations
  chord.alterations.forEach(alt => {
    if (alt === 'b5') {
        const idx = intervals.indexOf(7);
        if (idx !== -1) intervals[idx] = 6;
        else intervals.push(6);
    } else if (alt === '#5') {
        const idx = intervals.indexOf(7);
        if (idx !== -1) intervals[idx] = 8;
        else intervals.push(8);
    } else if (alt === 'b9') intervals.push(13);
    else if (alt === '#9') intervals.push(15);
    else if (alt === '#11') intervals.push(18);
    else if (alt === 'b13') intervals.push(20);
  });

  // Additions
  chord.additions.forEach(add => {
    if (add === 'add9') intervals.push(14);
    else if (add === 'add11') intervals.push(17);
    else if (add === 'add13') intervals.push(21);
  });

  const midiNotes = intervals.map(n => base + n);

  // Bass
  if (chord.bass) {
    const bassRoot = (rootMap[chord.bass] || 0) + (chord.bass_accidental === '#' ? 1 : chord.bass_accidental === 'b' ? -1 : 0);
    midiNotes.push(48 + bassRoot); // C3 base for bass
  } else {
    midiNotes.push(48 + root); // Add root as bass by default
  }

  return Array.from(new Set(midiNotes)).sort((a, b) => a - b);
};
