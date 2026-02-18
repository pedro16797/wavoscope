import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';

export const createConfigSlice: StateCreator<AppState, [], [], any> = (set, get) => ({
  themes: {
    dark: {
      name: 'dark',
      surface: '#121212',
      surfaceSecondary: '#1e1e1e',
      text: '#e0e0e0',
      accent: '#00aaff',
      grid: '#333333',
      playhead: '#ff4444',
      flagRhythm: '#ff4757',
      flagHarmony: '#00aaff',
      keyWhite: '#fff',
      keyBlack: '#333',
      spectrum: '#00ff00'
    }
  },
  currentTheme: 'dark',
  metronome_enabled: true,
  click_volume: 0.3,
  spectrum_keys: 37,
  default_output_folder: '',
  musicxml_author: '',
  showSettings: false,
  showLyrics: false,
  filter_enabled: false,
  filter_low_enabled: false,
  filter_high_enabled: false,
  filter_low_hz: 100,
  filter_high_hz: 5000,

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
        default_output_folder: res.data.default_output_folder,
        musicxml_author: res.data.musicxml_author
      });
    } catch (e) {
      console.error("[Store] Failed to fetch config:", e);
    }
  },

  setTheme: async (name: string) => {
    try {
        await axios.post(`${API_BASE}/config`, { theme: name });
        set({ currentTheme: name });
    } catch (e) {
        console.error("[Store] Failed to set theme:", e);
    }
  },

  updateMetronome: async (enabled?: boolean, volume?: number) => {
    try {
        await axios.post(`${API_BASE}/playback/metronome`, { enabled, volume });
        if (enabled !== undefined) set({ metronome_enabled: enabled });
        if (volume !== undefined) set({ click_volume: volume });
    } catch (e) {
        console.error("[Store] Failed to update metronome:", e);
    }
  },

  updateConfig: async (cfg: any) => {
    try {
        await axios.post(`${API_BASE}/config`, cfg);
        set(cfg);
    } catch (e) {
        console.error("[Store] Failed to update config:", e);
    }
  },

  setShowSettings: (show: boolean) => set({ showSettings: show }),
  setShowLyrics: (show: boolean) => set({ showLyrics: show }),
  updateFilter: async (filter: any) => {
    try {
        await axios.post(`${API_BASE}/playback/filter`, filter);
        set(filter);
    } catch (e) {
        console.error("[Store] Failed to update filter:", e);
    }
  },
});
