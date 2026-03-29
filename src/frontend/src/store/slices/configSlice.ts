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
  ui_scale: 1.0,
  spectrum_keys: 37,
  default_output_folder: '',
  musicxml_author: '',
  audio_device: '',
  autosave_enabled: true,
  autosave_forced: false,
  autosave_interval: 5,
  autosave_max_snapshots: 5,
  autosave_path: '',
  undo_steps: 50,
  remote_access: false,
  remote_url: '',
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
        click_volume: res.data.click_volume,
        ui_scale: res.data.ui_scale,
        spectrum_keys: newKeys,
        default_output_folder: res.data.default_output_folder,
        musicxml_author: res.data.musicxml_author,
        audio_device: res.data.audio_device,
        autosave_enabled: res.data.autosave_enabled,
        autosave_forced: res.data.autosave_forced,
        autosave_interval: res.data.autosave_interval,
        autosave_max_snapshots: res.data.autosave_max_snapshots,
        autosave_path: res.data.autosave_path,
        undo_steps: res.data.undo_steps,
        remote_access: res.data.remote_access
      };

      const maxShift = 6 - Math.floor(newKeys / 12);
      let effectiveShift = oldState.octave_shift;
      if (effectiveShift > maxShift) {
        effectiveShift = maxShift;
        updates.octave_shift = effectiveShift;
      }

      if (res.data.language) {
          updates.language = res.data.language;
          if (res.data.language !== i18n.language) {
              i18n.changeLanguage(res.data.language);
          }
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
        if (cfg.ui_scale !== undefined) set({ ui_scale: cfg.ui_scale });
        if (cfg.click_volume !== undefined) set({ click_volume: cfg.click_volume });
        if (cfg.default_output_folder !== undefined) set({ default_output_folder: cfg.default_output_folder });
        if (cfg.musicxml_author !== undefined) set({ musicxml_author: cfg.musicxml_author });
        if (cfg.audio_device !== undefined) set({ audio_device: cfg.audio_device });
        if (cfg.autosave_enabled !== undefined) set({ autosave_enabled: cfg.autosave_enabled });
        if (cfg.autosave_forced !== undefined) set({ autosave_forced: cfg.autosave_forced });
        if (cfg.autosave_interval !== undefined) set({ autosave_interval: cfg.autosave_interval });
        if (cfg.autosave_max_snapshots !== undefined) set({ autosave_max_snapshots: cfg.autosave_max_snapshots });
        if (cfg.autosave_path !== undefined) set({ autosave_path: cfg.autosave_path });
        if (cfg.undo_steps !== undefined) set({ undo_steps: cfg.undo_steps });
        if (cfg.remote_access !== undefined) set({ remote_access: cfg.remote_access });

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
                    high_enabled: newState.filter_high_enabled,
                    auto_gain: newState.filter_auto_gain
                }).catch(e => console.error("[Store] Failed to update filter after zoom change:", e));
            }
        }
    } catch (e) {
        console.error("[Store] Failed to update config:", e);
    }
  },

  browseFolder: async (initialDir?: string) => {
    const pywindow = window as any;
    if (pywindow.pywebview?.api?.browse_folder) {
        return await pywindow.pywebview.api.browse_folder(initialDir || '');
    }
    return null;
  },

  setShowSettings: (show: boolean) => set({ showSettings: show }),
  setShowSpectrum: (show: boolean) => set({ showSpectrum: show }),
  setShowLyrics: (show: boolean) => set({ showLyrics: show }),
  setViewport: (offset: number, zoom: number) => set({ offset, zoom }),

  fetchRemoteUrl: async () => {
    try {
        const res = await axios.get(`${API_BASE}/config/remote-url`);
        set({ remote_url: res.data.url });
    } catch (e) {
        console.error("[Store] Failed to fetch remote url:", e);
    }
  },
});
