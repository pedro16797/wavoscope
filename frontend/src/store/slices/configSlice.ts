import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';
import { midiToFreq, freqToMidi } from '../utils';

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
      set({ themes: res.data });
    } catch (e) {
      console.error("[Store] Failed to fetch themes:", e);
    }
  },

  fetchConfig: async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      const oldState = get();
      const newKeys = res.data.spectrum_keys;

      const updates: any = {
        currentTheme: res.data.theme,
        click_volume: res.data.click_volume,
        spectrum_keys: newKeys,
        high_quality_enhancement: res.data.high_quality_enhancement,
        default_output_folder: res.data.default_output_folder,
        musicxml_author: res.data.musicxml_author
      };

      const maxShift = 6 - Math.floor(newKeys / 12);
      let effectiveShift = oldState.octave_shift;
      if (effectiveShift > maxShift) {
        effectiveShift = maxShift;
        updates.octave_shift = effectiveShift;
      }

      if (newKeys !== oldState.spectrum_keys || effectiveShift !== oldState.octave_shift) {
        const oldBaseMidi = 48 + oldState.octave_shift * 12;
        const newBaseMidi = 48 + effectiveShift * 12;

        const ratioLow = (freqToMidi(oldState.filter_low_hz) - oldBaseMidi) / oldState.spectrum_keys;
        updates.filter_low_hz = midiToFreq(newBaseMidi + ratioLow * newKeys);
        const ratioHigh = (freqToMidi(oldState.filter_high_hz) - oldBaseMidi) / oldState.spectrum_keys;
        updates.filter_high_hz = midiToFreq(newBaseMidi + ratioHigh * newKeys);
      }

      set(updates);
    } catch (e) {
      console.error("[Store] Failed to fetch config:", e);
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
        const oldState = get();
        await axios.post(`${API_BASE}/config`, cfg);
        if (cfg.theme) set({ currentTheme: cfg.theme });
        if (cfg.click_volume !== undefined) set({ click_volume: cfg.click_volume });
        if (cfg.high_quality_enhancement !== undefined) set({ high_quality_enhancement: cfg.high_quality_enhancement });
        if (cfg.default_output_folder !== undefined) set({ default_output_folder: cfg.default_output_folder });
        if (cfg.musicxml_author !== undefined) set({ musicxml_author: cfg.musicxml_author });

        if (cfg.spectrum_keys !== undefined && cfg.spectrum_keys !== oldState.spectrum_keys) {
            const newKeys = cfg.spectrum_keys;
            const updates: any = { spectrum_keys: newKeys };

            const maxShift = 6 - Math.floor(newKeys / 12);
            let effectiveShift = oldState.octave_shift;
            if (effectiveShift > maxShift) {
                effectiveShift = maxShift;
                updates.octave_shift = effectiveShift;
            }

            const oldBaseMidi = 48 + oldState.octave_shift * 12;
            const newBaseMidi = 48 + effectiveShift * 12;

            const ratioLow = (freqToMidi(oldState.filter_low_hz) - oldBaseMidi) / oldState.spectrum_keys;
            updates.filter_low_hz = midiToFreq(newBaseMidi + ratioLow * newKeys);

            const ratioHigh = (freqToMidi(oldState.filter_high_hz) - oldBaseMidi) / oldState.spectrum_keys;
            updates.filter_high_hz = midiToFreq(newBaseMidi + ratioHigh * newKeys);

            set(updates);

            if ((oldState.filter_low_enabled && updates.filter_low_hz) || (oldState.filter_high_enabled && updates.filter_high_hz)) {
                const newState = get();
                axios.post(`${API_BASE}/playback/filter`, {
                    enabled: newState.filter_enabled,
                    low_hz: newState.filter_low_hz,
                    high_hz: newState.filter_high_hz,
                    low_enabled: newState.filter_low_enabled,
                    high_enabled: newState.filter_high_enabled
                }).catch(e => console.error("[Store] Failed to update filter after zoom change:", e));
            }
        }
    } catch (e) {
        console.error("[Store] Failed to update config:", e);
    }
  },

  setShowSettings: (show) => set({ showSettings: show }),
});
