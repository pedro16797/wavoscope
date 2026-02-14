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
  themes: Record<string, any>;
  currentTheme: string;

  fetchStatus: () => Promise<void>;
  fetchThemes: () => Promise<void>;
  controlPlayback: (action: string, value?: number) => Promise<void>;
  browseFile: () => Promise<void>;
  setTheme: (name: string) => void;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
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
  themes: {},
  currentTheme: 'dark',

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

  controlPlayback: async (action, value) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed') set({ speed: value });
      if (action === 'set_volume') set({ volume: value });
    } catch (e) {
      console.error(e);
    }
  },

  browseFile: async () => {
    try {
      const res = await axios.get(`${API_BASE}/browse`);
      if (res.data.status === 'loaded') {
        get().fetchStatus();
      }
    } catch (e) {
      console.error(e);
    }
  },

  setTheme: (name) => {
    set({ currentTheme: name });
  },

  updatePosition: (pos) => {
    set({ position: pos });
  },

  setPlaying: (playing) => {
    set({ playing });
  }
}));
