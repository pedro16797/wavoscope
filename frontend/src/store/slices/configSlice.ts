import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';

export interface ConfigSlice {
  themes: Record<string, Record<string, string>>;
  currentTheme: string;
  metronome_enabled: boolean;
  click_volume: number;
  spectrum_keys: number;
  high_quality_enhancement: boolean;
  default_output_folder: string;
  musicxml_author: string;
  showSettings: boolean;

  fetchThemes: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  setTheme: (name: string) => Promise<void>;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: {
    theme?: string,
    click_volume?: number,
    spectrum_keys?: number,
    high_quality_enhancement?: boolean,
    default_output_folder?: string,
    musicxml_author?: string
  }) => Promise<void>;
  setShowSettings: (show: boolean) => void;
}

export const createConfigSlice: StateCreator<AppState, [], [], ConfigSlice> = (set, get) => ({
  themes: {},
  currentTheme: 'dark',
  metronome_enabled: true,
  click_volume: 0.3,
  spectrum_keys: 37,
  high_quality_enhancement: false,
  default_output_folder: '',
  musicxml_author: '',
  showSettings: false,

  fetchThemes: async () => {
    try {
      const res = await axios.get(`${API_BASE}/themes`);
      set({ themes: res.data } as any);
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
        high_quality_enhancement: res.data.high_quality_enhancement,
        default_output_folder: res.data.default_output_folder,
        musicxml_author: res.data.musicxml_author
      } as any);
    } catch (e) {
      console.error("[Store] Failed to fetch config:", e);
    }
  },

  setTheme: async (name) => {
    try {
        await axios.post(`${API_BASE}/config`, { theme: name });
        set({ currentTheme: name } as any);
    } catch (e) {
        console.error("[Store] Failed to set theme:", e);
    }
  },

  updateMetronome: async (enabled, volume) => {
    try {
        await axios.post(`${API_BASE}/playback/metronome`, { enabled, volume });
        if (enabled !== undefined) set({ metronome_enabled: enabled } as any);
        if (volume !== undefined) set({ click_volume: volume } as any);
    } catch (e) {
        console.error("[Store] Failed to update metronome:", e);
    }
  },

  updateConfig: async (cfg) => {
    try {
        await axios.post(`${API_BASE}/config`, cfg);
        if (cfg.theme) set({ currentTheme: cfg.theme } as any);
        if (cfg.click_volume !== undefined) set({ click_volume: cfg.click_volume } as any);
        if (cfg.spectrum_keys !== undefined) set({ spectrum_keys: cfg.spectrum_keys } as any);
        if (cfg.high_quality_enhancement !== undefined) set({ high_quality_enhancement: cfg.high_quality_enhancement } as any);
        if (cfg.default_output_folder !== undefined) set({ default_output_folder: cfg.default_output_folder } as any);
        if (cfg.musicxml_author !== undefined) set({ musicxml_author: cfg.musicxml_author } as any);
        if (cfg.spectrum_keys !== undefined) get().ensureFiltersVisible();
    } catch (e) {
        console.error("[Store] Failed to update config:", e);
    }
  },

  setShowSettings: (show) => set({ showSettings: show } as any),
});
