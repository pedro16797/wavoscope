import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';
import { midiToFreq, freqToMidi } from '../utils';

export interface PlaybackSlice {
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
  loop_mode: string;
  loop_range: [number, number];
  filter_enabled: boolean;
  filter_low_enabled: boolean;
  filter_high_enabled: boolean;
  filter_low_hz: number;
  filter_high_hz: number;
  fft_window: number;
  octave_shift: number;

  controlPlayback: (action: string, value?: number) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  setLoopMode: (mode: string) => Promise<void>;
  updateFilter: (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean }) => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;
  playTone: (freq: number, action: 'start' | 'stop') => Promise<void>;
  stopAllTones: () => Promise<void>;
}

export const createPlaybackSlice: StateCreator<AppState, [], [], PlaybackSlice> = (set, get) => ({
  position: 0,
  duration: 0,
  playing: false,
  speed: 1.0,
  volume: 1.0,
  loop_mode: 'none',
  loop_range: [0, 0],
  filter_enabled: true,
  filter_low_enabled: false,
  filter_high_enabled: false,
  filter_low_hz: midiToFreq(48 + 37 * 0.1),
  filter_high_hz: midiToFreq(48 + 37 * 0.9),
  fft_window: 0.3,
  octave_shift: 0,

  controlPlayback: async (action: string, value?: number) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value });
      if (action === 'set_volume' && value !== undefined) set({ volume: value });
    } catch (e) {
      console.error(`[Store] Failed to control playback (${action}):`, e);
    }
  },

  updatePosition: (pos: number) => {
    set({ position: pos });
  },

  setPlaying: (playing: boolean) => {
    set({ playing });
  },

  setLoopMode: async (mode: string) => {
    try {
        await axios.post(`${API_BASE}/playback/loop`, { mode });
        set({ loop_mode: mode });
        await get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to set loop mode:", e);
    }
  },

  cycleLoopMode: async () => {
    const state = get();
    const modes = ['none', 'lyric', 'section', 'bar', 'whole'];

    const isAvailable = (mode: string) => {
        if (mode === 'none' || mode === 'whole') return true;
        if (mode === 'lyric') return state.selectedLyricIdx !== null;
        if (mode === 'section') return state.flags.some(f => f.is_section_start && f.t <= state.position);
        if (mode === 'bar') return state.flags.some(f => f.type === 'rhythm' && f.t <= state.position);
        return false;
    };

    let nextMode = 'none';
    const currentIdx = modes.indexOf(state.loop_mode);
    for (let i = 1; i < modes.length; i++) {
        const candidate = modes[(currentIdx + i) % modes.length];
        if (isAvailable(candidate)) {
            nextMode = candidate;
            break;
        }
    }
    await state.setLoopMode(nextMode);
  },

  updateFilter: async (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean }) => {
    const oldState = get();
    const updates: any = {};

    if (filter.enabled !== undefined) updates.filter_enabled = filter.enabled;
    if (filter.low_hz !== undefined) updates.filter_low_hz = filter.low_hz;
    if (filter.high_hz !== undefined) updates.filter_high_hz = filter.high_hz;
    if (filter.low_enabled !== undefined) updates.filter_low_enabled = filter.low_enabled;
    if (filter.high_enabled !== undefined) updates.filter_high_enabled = filter.high_enabled;
    set(updates);

    const shouldUpdateBackend =
        filter.low_enabled !== undefined ||
        filter.high_enabled !== undefined ||
        filter.enabled !== undefined ||
        (filter.low_hz !== undefined && oldState.filter_low_enabled) ||
        (filter.high_hz !== undefined && oldState.filter_high_enabled);

    if (shouldUpdateBackend) {
        const newState = get();
        const payload = {
            enabled: newState.filter_enabled,
            low_hz: newState.filter_low_hz,
            high_hz: newState.filter_high_hz,
            low_enabled: newState.filter_low_enabled,
            high_enabled: newState.filter_high_enabled
        };
        try {
            await axios.post(`${API_BASE}/playback/filter`, payload);
        } catch (e) {
            console.error("[Store] Failed to update filter:", e);
        }
    }
  },

  playTone: async (freq: number, action: 'start' | 'stop') => {
    try {
        await axios.post(`${API_BASE}/playback/tone`, { freq, action });
    } catch (e) {
        console.error("[Store] Failed to play tone:", e);
    }
  },

  stopAllTones: async () => {
    try {
        await axios.post(`${API_BASE}/playback/tone`, { freq: 0, action: 'stop' });
    } catch (e) {
        console.error("[Store] Failed to stop all tones:", e);
    }
  },

  setFFTWindow: (sec: number) => set({ fft_window: sec }),
  setOctaveShift: (shift: number) => {
    const state = get();
    const maxShift = 6 - Math.floor(state.spectrum_keys / 12);
    const clampedShift = Math.max(-2, Math.min(maxShift, shift));
    const oldShift = state.octave_shift;
    if (clampedShift === oldShift) return;

    const updates: any = { octave_shift: clampedShift };
    const oldBaseMidi = 48 + oldShift * 12;
    const newBaseMidi = 48 + clampedShift * 12;

    const ratioLow = (freqToMidi(state.filter_low_hz) - oldBaseMidi) / state.spectrum_keys;
    updates.filter_low_hz = midiToFreq(newBaseMidi + ratioLow * state.spectrum_keys);
    const ratioHigh = (freqToMidi(state.filter_high_hz) - oldBaseMidi) / state.spectrum_keys;
    updates.filter_high_hz = midiToFreq(newBaseMidi + ratioHigh * state.spectrum_keys);

    set(updates);

    if ((state.filter_low_enabled && updates.filter_low_hz) || (state.filter_high_enabled && updates.filter_high_hz)) {
        const newState = get();
        axios.post(`${API_BASE}/playback/filter`, {
            enabled: newState.filter_enabled,
            low_hz: newState.filter_low_hz,
            high_hz: newState.filter_high_hz,
            low_enabled: newState.filter_low_enabled,
            high_enabled: newState.filter_high_enabled
        }).catch(e => console.error("[Store] Failed to update filter after octave shift:", e));
    }
  },
});
