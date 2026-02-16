import { create } from 'zustand';
import axios from 'axios';

export const API_BASE = window.location.origin.includes(':5173') ? 'http://127.0.0.1:8000' : '';

export interface Flag {
  t: number;
  type: string;
  subdivision: number;
  name: string;
  is_section_start: boolean;
  shaded_subdivisions: boolean;
  auto_name?: string;
}

export interface Chord {
  root: string;
  accidental: string;
  quality: string;
  extension: string;
  alterations: string[];
  additions: string[];
  bass: string;
  bass_accidental: string;
}

export interface HarmonyFlag {
  t: number;
  chord: Chord;
}

export const midiToFreq = (midi: number) => 440.0 * Math.pow(2, (midi - 69) / 12);

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

interface AppState {
  loaded: boolean;
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
  filename: string;
  flags: Flag[];
  harmony_flags: HarmonyFlag[];
  dirty: boolean;
  metronome_enabled: boolean;
  click_volume: number;
  loop_mode: string;
  loop_range: [number, number];
  filter_enabled: boolean;
  filter_low_enabled: boolean;
  filter_high_enabled: boolean;
  filter_low_hz: number;
  filter_high_hz: number;
  themes: Record<string, Record<string, string>>;
  currentTheme: string;
  spectrum_keys: number;
  high_quality_enhancement: boolean;
  fft_window: number;
  octave_shift: number;

  // UI State
  showSettings: boolean;
  editingFlagIdx: number | null;
  editingHarmonyFlagIdx: number | null;

  fetchStatus: () => Promise<void>;
  fetchThemes: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  controlPlayback: (action: string, value?: number) => Promise<void>;
  browseFile: () => Promise<void>;
  setTheme: (name: string) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: { theme?: string, click_volume?: number, spectrum_keys?: number, high_quality_enhancement?: boolean }) => Promise<void>;
  addFlag: (t: number) => Promise<void>;
  moveFlag: (idx: number, t: number) => Promise<void>;
  removeFlag: (idx: number) => Promise<void>;
  setLoopMode: (mode: string) => Promise<void>;
  updateFilter: (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean }) => Promise<void>;

  addHarmonyFlag: (t: number, chord?: Chord) => Promise<HarmonyFlag | null>;
  moveHarmonyFlag: (idx: number, t: number) => Promise<void>;
  removeHarmonyFlag: (idx: number) => Promise<void>;
  updateHarmonyFlag: (idx: number, t: number, chord: Chord) => Promise<void>;
  analyzeChord: (t: number) => Promise<Chord>;

  saveProject: () => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;

  setShowSettings: (show: boolean) => void;
  setEditingFlagIdx: (idx: number | null) => void;
  setEditingHarmonyFlagIdx: (idx: number | null) => void;
}

export const useStore = create<AppState>((set, get) => ({
  loaded: false,
  position: 0,
  duration: 0,
  playing: false,
  speed: 1.0,
  volume: 1.0,
  filename: '',
  flags: [],
  harmony_flags: [],
  dirty: false,
  metronome_enabled: true,
  click_volume: 0.3,
  loop_mode: 'none',
  loop_range: [0, 0],
  filter_enabled: false,
  filter_low_enabled: true,
  filter_high_enabled: true,
  filter_low_hz: 200,
  filter_high_hz: 2000,
  themes: {},
  currentTheme: 'dark',
  spectrum_keys: 37,
  high_quality_enhancement: false,
  fft_window: 0.3,
  octave_shift: 0,

  showSettings: false,
  editingFlagIdx: null,
  editingHarmonyFlagIdx: null,

  fetchStatus: async () => {
    try {
      const res = await axios.get(`${API_BASE}/status`);
      set(res.data);
    } catch (e) {
      console.error("[Store] Failed to fetch status:", e);
    }
  },

  fetchThemes: async () => {
    try {
      const res = await axios.get(`${API_BASE}/themes`);
      set({ themes: res.data });
    } catch (e) {
      console.error("[Store] Failed to fetch themes:", e);
    }
  },

  fetchConfig: async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      set({
        currentTheme: res.data.theme,
        click_volume: res.data.click_volume,
        spectrum_keys: res.data.spectrum_keys,
        high_quality_enhancement: res.data.high_quality_enhancement
      });
    } catch (e) {
      console.error("[Store] Failed to fetch config:", e);
    }
  },

  controlPlayback: async (action, value) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value });
      if (action === 'set_volume' && value !== undefined) set({ volume: value });
    } catch (e) {
      console.error(`[Store] Failed to control playback (${action}):`, e);
    }
  },

  browseFile: async () => {
    const pywindow = window as Window & { pywebview?: { api: { browse: () => Promise<void> } } };
    try {
      if (pywindow.pywebview?.api?.browse) {
        await pywindow.pywebview.api.browse();
        await get().fetchStatus();
      } else {
        const res = await axios.get(`${API_BASE}/browse`);
        if (res.data.status === 'loaded') {
          await get().fetchStatus();
        }
      }
    } catch (e) {
      console.error("[Store] Failed to browse or load file:", e);
    }
  },

  setTheme: async (name) => {
    try {
        await axios.post(`${API_BASE}/config`, { theme: name });
        set({ currentTheme: name });
    } catch (e) {
        console.error("[Store] Failed to set theme:", e);
    }
  },

  addHarmonyFlag: async (t, chord) => {
    try {
        if (!chord) {
            chord = await get().analyzeChord(t);
        }
        await axios.post(`${API_BASE}/project/harmony_flags`, { t, chord });
        await get().fetchStatus();
        return { t, chord };
    } catch (e) {
        console.error("[Store] Failed to add harmony flag:", e);
        return null;
    }
  },

  moveHarmonyFlag: async (idx, t) => {
    try {
        await axios.post(`${API_BASE}/project/harmony_flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move harmony flag:", e);
    }
  },

  removeHarmonyFlag: async (idx) => {
    try {
        await axios.delete(`${API_BASE}/project/harmony_flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove harmony flag:", e);
    }
  },

  updateHarmonyFlag: async (idx, t, chord) => {
    try {
        await axios.patch(`${API_BASE}/project/harmony_flags/${idx}`, { t, chord });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to update harmony flag:", e);
    }
  },

  analyzeChord: async (t) => {
    try {
        const res = await axios.get(`${API_BASE}/project/analyze_chord`, { params: { t } });
        return res.data;
    } catch (e) {
        console.error("[Store] Failed to analyze chord:", e);
        return {
            root: 'C',
            accidental: '',
            quality: 'M',
            extension: '',
            alterations: [],
            additions: [],
            bass: '',
            bass_accidental: ''
        };
    }
  },

  updatePosition: (pos) => {
    set({ position: pos });
  },

  setPlaying: (playing) => {
    set({ playing });
  },

  updateMetronome: async (enabled, volume) => {
    try {
        await axios.post(`${API_BASE}/playback/metronome`, { enabled, volume });
        if (enabled !== undefined) set({ metronome_enabled: enabled });
        if (volume !== undefined) set({ click_volume: volume });
    } catch (e) {
        console.error("[Store] Failed to update metronome:", e);
    }
  },

  updateConfig: async (cfg) => {
    try {
        await axios.post(`${API_BASE}/config`, cfg);
        if (cfg.theme) set({ currentTheme: cfg.theme });
        if (cfg.click_volume !== undefined) set({ click_volume: cfg.click_volume });
        if (cfg.spectrum_keys !== undefined) set({ spectrum_keys: cfg.spectrum_keys });
        if (cfg.high_quality_enhancement !== undefined) set({ high_quality_enhancement: cfg.high_quality_enhancement });
    } catch (e) {
        console.error("[Store] Failed to update config:", e);
    }
  },

  addFlag: async (t) => {
    try {
        await axios.post(`${API_BASE}/project/flags`, { t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to add flag:", e);
    }
  },

  moveFlag: async (idx, t) => {
    try {
        await axios.post(`${API_BASE}/project/flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move flag:", e);
    }
  },

  removeFlag: async (idx) => {
    try {
        await axios.delete(`${API_BASE}/project/flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove flag:", e);
    }
  },

  setLoopMode: async (mode) => {
    try {
        await axios.post(`${API_BASE}/playback/loop`, { mode });
        set({ loop_mode: mode });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to set loop mode:", e);
    }
  },

  updateFilter: async (filter) => {
    const state = get();
    // Optimistic update
    const updates: Partial<AppState> = {};

    if (filter.enabled === true && !state.filter_enabled) {
      // Filter is being enabled. Check bounds.
      const baseMidi = 48 + state.octave_shift * 12;
      const lowBound = midiToFreq(baseMidi);
      const highBound = midiToFreq(baseMidi + state.spectrum_keys);

      // If current values are outside, reset them to be visible
      if (state.filter_low_hz < lowBound || state.filter_low_hz > highBound ||
          state.filter_high_hz < lowBound || state.filter_high_hz > highBound) {
        updates.filter_low_hz = midiToFreq(baseMidi + state.spectrum_keys * 0.3);
        updates.filter_high_hz = midiToFreq(baseMidi + state.spectrum_keys * 0.7);
        // Also update the filter object for the API call
        filter.low_hz = updates.filter_low_hz;
        filter.high_hz = updates.filter_high_hz;
      }
    }

    if (filter.enabled !== undefined) updates.filter_enabled = filter.enabled;
    if (filter.low_hz !== undefined) updates.filter_low_hz = filter.low_hz;
    if (filter.high_hz !== undefined) updates.filter_high_hz = filter.high_hz;
    if (filter.low_enabled !== undefined) updates.filter_low_enabled = filter.low_enabled;
    if (filter.high_enabled !== undefined) updates.filter_high_enabled = filter.high_enabled;
    set(updates);

    try {
        await axios.post(`${API_BASE}/playback/filter`, filter);
    } catch (e) {
        console.error("[Store] Failed to update filter:", e);
    }
  },

  saveProject: async () => {
    try {
        await axios.post(`${API_BASE}/project/save`);
        set({ dirty: false });
    } catch (e) {
        console.error("[Store] Failed to save project:", e);
    }
  },

  setFFTWindow: (sec) => set({ fft_window: sec }),
  setOctaveShift: (shift) => set({ octave_shift: shift }),

  setShowSettings: (show) => set({ showSettings: show }),
  setEditingFlagIdx: (idx) => set({ editingFlagIdx: idx }),
  setEditingHarmonyFlagIdx: (idx) => set({ editingHarmonyFlagIdx: idx })
}));
