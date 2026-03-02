import type { Chord } from './types';

export const midiToFreq = (midi: number) => 440.0 * Math.pow(2, (midi - 69) / 12);
export const freqToMidi = (freq: number) => 12 * Math.log2(freq / 440) + 69;

export const formatChord = (chord: Chord): string => {
  let s = chord.r + chord.ca;
  if (chord.q !== 'M' && chord.q !== '') s += chord.q;
  s += chord.ext;
  chord.alt.forEach(a => s += a);
  chord.add.forEach(a => s += a);
  if (chord.b) s += '/' + chord.b + chord.ba;
  return s;
};

export const getChordMidiNotes = (chord: Chord): number[] => {
  const rootMap: Record<string, number> = { 'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11 };
  const root = (rootMap[chord.r] || 0) + (chord.ca === '#' ? 1 : chord.ca === 'b' ? -1 : 0);
  const base = 60 + root; // C4 base

  const intervals: number[] = [0]; // Intervals relative to root

  // Quality
  if (chord.q === 'm') intervals.push(3, 7);
  else if (chord.q === 'dim') intervals.push(3, 6);
  else if (chord.q === 'aug') intervals.push(4, 8);
  else if (chord.q === 'sus2') intervals.push(2, 7);
  else if (chord.q === 'sus4') intervals.push(5, 7);
  else intervals.push(4, 7); // Default to Major

  // Extension
  if (chord.ext === '7') {
    if (chord.q === 'dim') intervals.push(9); // Full dim
    else intervals.push(10); // dominant/minor 7th
  } else if (chord.ext === '9') {
    intervals.push(chord.q === 'dim' ? 9 : 10, 14);
  } else if (chord.ext === '11') {
    intervals.push(chord.q === 'dim' ? 9 : 10, 14, 17);
  } else if (chord.ext === '13') {
    intervals.push(chord.q === 'dim' ? 9 : 10, 14, 17, 21);
  }

  // Alterations
  chord.alt.forEach(alt_val => {
    if (alt_val === 'b5') {
        const idx = intervals.indexOf(7);
        if (idx !== -1) intervals[idx] = 6;
        else intervals.push(6);
    } else if (alt_val === '#5') {
        const idx = intervals.indexOf(7);
        if (idx !== -1) intervals[idx] = 8;
        else intervals.push(8);
    } else if (alt_val === 'b9') intervals.push(13);
    else if (alt_val === '#9') intervals.push(15);
    else if (alt_val === '#11') intervals.push(18);
    else if (alt_val === 'b13') intervals.push(20);
  });

  // Additions
  chord.add.forEach(add_val => {
    if (add_val === 'add9') intervals.push(14);
    else if (add_val === 'add11') intervals.push(17);
    else if (add_val === 'add13') intervals.push(21);
  });

  const midiNotes = intervals.map(n => base + n);

  // Bass
  if (chord.b) {
    const bassRoot = (rootMap[chord.b] || 0) + (chord.ba === '#' ? 1 : chord.ba === 'b' ? -1 : 0);
    midiNotes.push(48 + bassRoot); // C3 base for bass
  } else {
    midiNotes.push(48 + root); // Add root as bass by default
  }

  return Array.from(new Set(midiNotes)).sort((a, b) => a - b);
};

export const getTimelineStep = (span: number): number => {
  const target = span / 5;
  if (target <= 0) return 1;

  if (target < 30) {
    const p10 = Math.pow(10, Math.floor(Math.log10(target)));
    if (target >= 5 * p10) return 5 * p10;
    return p10;
  }

  if (target < 3600) {
    const specials = [30, 60, 300, 600, 1800];
    for (let i = specials.length - 1; i >= 0; i--) {
      if (target >= specials[i]) return specials[i];
    }
    return 30;
  }

  const hours = target / 3600;
  const p10 = Math.pow(10, Math.floor(Math.log10(hours)));
  if (hours >= 5 * p10) return 5 * p10 * 3600;
  return p10 * 3600;
};

export const formatTimelineLabel = (t: number, step: number): string => {
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const s = Math.floor(t % 60);

  let label = "";
  if (h > 0) {
    label = `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  } else {
    label = `${m}:${s.toString().padStart(2, '0')}`;
  }

  if (step < 1) {
    const decimals = Math.max(1, Math.ceil(-Math.log10(step + 1e-9)));
    const part = (t % 1).toFixed(decimals).split('.')[1];
    label += "." + part;
  }
  return label;
};
