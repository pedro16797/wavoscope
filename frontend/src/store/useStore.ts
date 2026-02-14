import { create } from 'zustand';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export interface Flag {
  t: number;
  type: string;
  subdivision: number;
  name: string;
  is_section_start: boolean;
  shaded_subdivisions: boolean;
  auto_name?: string;
}

interface AppState {
  loaded: boolean;
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
  filename: string;
  flags: Flag[];
  dirty: boolean;
  metronome_enabled: boolean;
  click_gain: number;
  themes: Record<string, any>;
  currentTheme: string;
  spectrum_keys: number;
  fft_window: number;
  octave_shift: number;

  // UI State
  showSettings: boolean;
  editingFlagIdx: number | null;

  fetchStatus: () => Promise<void>;
  fetchThemes: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  controlPlayback: (action: string, value?: number) => Promise<void>;
  browseFile: () => Promise<void>;
  setTheme: (name: string) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: { theme?: string, click_volume?: number, spectrum_keys?: number }) => Promise<void>;
  addFlag: (t: number) => Promise<void>;
  moveFlag: (idx: number, t: number) => Promise<void>;
  removeFlag: (idx: number) => Promise<void>;
  saveProject: () => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;

  setShowSettings: (show: boolean) => void;
  setEditingFlagIdx: (idx: number | null) => void;
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
  dirty: false,
  metronome_enabled: true,
  click_gain: 0.3,
  themes: {},
  currentTheme: 'dark',
  spectrum_keys: 37,
  fft_window: 0.3,
  octave_shift: 0,

  showSettings: false,
  editingFlagIdx: null,

  fetchStatus: async () => {
    try {
      const res = await axios.get(`${API_BASE}/status`);
      set(res.data);
    } catch (e) {
      console.error(e);
    }
  },

  fetchThemes: async () => {
    try {
      const res = await axios.get(`${API_BASE}/themes`);
      set({ themes: res.data });
    } catch (e) {
      console.error(e);
    }
  },

  fetchConfig: async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      set({
        currentTheme: res.data.theme,
        click_gain: res.data.click_volume,
        spectrum_keys: res.data.spectrum_keys
      });
    } catch (e) {
      console.error(e);
    }
  },

  controlPlayback: async (action, value) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value });
      if (action === 'set_volume' && value !== undefined) set({ volume: value });
    } catch (e) {
      console.error(e);
    }
  },

  browseFile: async () => {
    try {
      if ((window as any).pywebview?.api?.browse) {
        await (window as any).pywebview.api.browse();
        get().fetchStatus();
      } else {
        const res = await axios.get(`${API_BASE}/browse`);
        if (res.data.status === 'loaded') {
          get().fetchStatus();
        }
      }
    } catch (e) {
      console.error(e);
    }
  },

  setTheme: async (name) => {
    try {
        await axios.post(`${API_BASE}/config`, { theme: name });
        set({ currentTheme: name });
    } catch (e) {
        console.error(e);
    }
  },

  updatePosition: (pos) => {
    set({ position: pos });
  },

  setPlaying: (playing) => {
    set({ playing });
  },

  updateMetronome: async (enabled, gain) => {
    try {
        await axios.post(`${API_BASE}/playback/metronome`, { enabled, gain });
        if (enabled !== undefined) set({ metronome_enabled: enabled });
        if (gain !== undefined) set({ click_gain: gain });
    } catch (e) {
        console.error(e);
    }
  },

  updateConfig: async (cfg) => {
    try {
        await axios.post(`${API_BASE}/config`, cfg);
        if (cfg.theme) set({ currentTheme: cfg.theme });
        if (cfg.click_volume !== undefined) set({ click_gain: cfg.click_volume });
        if (cfg.spectrum_keys !== undefined) set({ spectrum_keys: cfg.spectrum_keys });
    } catch (e) {
        console.error(e);
    }
  },

  addFlag: async (t) => {
    try {
        await axios.post(`${API_BASE}/project/flags`, { t });
        get().fetchStatus();
    } catch (e) {
        console.error(e);
    }
  },

  moveFlag: async (idx, t) => {
    try {
        await axios.post(`${API_BASE}/project/flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error(e);
    }
  },

  removeFlag: async (idx) => {
    try {
        await axios.delete(`${API_BASE}/project/flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error(e);
    }
  },

  saveProject: async () => {
    try {
        await axios.post(`${API_BASE}/project/save`);
        set({ dirty: false });
    } catch (e) {
        console.error(e);
    }
  },

  setFFTWindow: (sec) => set({ fft_window: sec }),
  setOctaveShift: (shift) => set({ octave_shift: shift }),

  setShowSettings: (show) => set({ showSettings: show }),
  setEditingFlagIdx: (idx) => set({ editingFlagIdx: idx })
}));
