import type { StateCreator } from 'zustand';
import axios from 'axios';
import i18n from '../../i18n';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';
import { midiToFreq, freqToMidi } from '../utils';

import type { ConfigSlice } from '../types';

export const createConfigSlice: StateCreator<AppState, [], [], ConfigSlice> = (set, get) => ({
  themes: {},
  currentTheme: 'dark',
  locales: [],
  audioDevices: [],
  language: 'en',
  metronome_enabled: true,
  click_volume: 0.3,
  spectrum_keys: 37,
  default_output_folder: '',
  musicxml_author: '',
  audio_device: '',
  showSettings: false,
  showSpectrum: true,
  showLyrics: false,
  offset: 0,
  zoom: 100,

  fetchThemes: async () => {
    try {
      const res = await axios.get(`${API_BASE}/themes`);
      set({ themes: res.data });
    } catch (e) {
      console.error("[Store] Failed to fetch themes:", e);
    }
  },

  fetchLocales: async () => {
    try {
      const res = await axios.get(`${API_BASE}/locales-api/list`);
      set({ locales: res.data });
    } catch (e) {
      console.error("[Store] Failed to fetch locales:", e);
    }
  },

  fetchAudioDevices: async () => {
    try {
      const res = await axios.get(`${API_BASE}/config/audio-devices`);
      set({ audioDevices: res.data });
    } catch (e) {
      console.error("[Store] Failed to fetch audio devices:", e);
    }
  },

  fetchConfig: async () => {
    try {
      const res = await axios.get(`${API_BASE}/config`);
      const oldState = get();
      const newKeys = res.data.spectrum_keys;

      const updates: any = {
        currentTheme: res.data.theme,
        language: res.data.language,
        click_volume: res.data.click_volume,
        spectrum_keys: newKeys,
        default_output_folder: res.data.default_output_folder,
        musicxml_author: res.data.musicxml_author,
        audio_device: res.data.audio_device
      };

      const maxShift = 6 - Math.floor(newKeys / 12);
      let effectiveShift = oldState.octave_shift;
      if (effectiveShift > maxShift) {
        effectiveShift = maxShift;
        updates.octave_shift = effectiveShift;
      }

      if (res.data.language && res.data.language !== i18n.language) {
        i18n.changeLanguage(res.data.language);
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

  updateMetronome: async (enabled?: boolean, volume?: number) => {
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
        if (cfg.language) {
            set({ language: cfg.language });
            i18n.changeLanguage(cfg.language);
        }
        if (cfg.click_volume !== undefined) set({ click_volume: cfg.click_volume });
        if (cfg.default_output_folder !== undefined) set({ default_output_folder: cfg.default_output_folder });
        if (cfg.musicxml_author !== undefined) set({ musicxml_author: cfg.musicxml_author });
        if (cfg.audio_device !== undefined) set({ audio_device: cfg.audio_device });

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

  browseFolder: async () => {
    const pywindow = window as any;
    if (pywindow.pywebview?.api?.browse_folder) {
        return await pywindow.pywebview.api.browse_folder();
    }
    return null;
  },

  setShowSettings: (show: boolean) => set({ showSettings: show }),
  setShowSpectrum: (show: boolean) => set({ showSpectrum: show }),
  setShowLyrics: (show: boolean) => set({ showLyrics: show }),
  setViewport: (offset: number, zoom: number) => set({ offset, zoom }),
});
