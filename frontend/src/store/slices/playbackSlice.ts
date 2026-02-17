import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';
import { midiToFreq } from '../utils';

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
  filter_low_hz: 200,
  filter_high_hz: 2000,
  fft_window: 0.3,
  octave_shift: 0,

  controlPlayback: async (action, value) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value } as any);
      if (action === 'set_volume' && value !== undefined) set({ volume: value } as any);
    } catch (e) {
      console.error(`[Store] Failed to control playback (${action}):`, e);
    }
  },

  updatePosition: (pos) => {
    set({ position: pos } as any);
  },

  setPlaying: (playing) => {
    set({ playing } as any);
  },

  setLoopMode: async (mode) => {
    try {
        await axios.post(`${API_BASE}/playback/loop`, { mode });
        set({ loop_mode: mode } as any);
        await get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to set loop mode:", e);
    }
  },

  updateFilter: async (filter) => {
    const oldState = get();
    const updates: any = {};

    // Recover auto-positioning logic when enabling handles for the first time or if they are out of bounds
    if ((filter.low_enabled === true && !oldState.filter_low_enabled) ||
        (filter.high_enabled === true && !oldState.filter_high_enabled)) {

        const baseMidi = 48 + oldState.octave_shift * 12;
        const lowBound = midiToFreq(baseMidi);
        const highBound = midiToFreq(baseMidi + oldState.spectrum_keys);

        if (oldState.filter_low_hz < lowBound || oldState.filter_low_hz > highBound ||
            oldState.filter_high_hz < lowBound || oldState.filter_high_hz > highBound) {

            updates.filter_low_hz = midiToFreq(baseMidi + oldState.spectrum_keys * 0.3);
            updates.filter_high_hz = midiToFreq(baseMidi + oldState.spectrum_keys * 0.7);

            // If they aren't provided in the call, use these calculated ones
            if (filter.low_hz === undefined) filter.low_hz = updates.filter_low_hz;
            if (filter.high_hz === undefined) filter.high_hz = updates.filter_high_hz;
        }
    }

    if (filter.enabled !== undefined) updates.filter_enabled = filter.enabled;
    if (filter.low_hz !== undefined) updates.filter_low_hz = filter.low_hz;
    if (filter.high_hz !== undefined) updates.filter_high_hz = filter.high_hz;
    if (filter.low_enabled !== undefined) updates.filter_low_enabled = filter.low_enabled;
    if (filter.high_enabled !== undefined) updates.filter_high_enabled = filter.high_enabled;
    set(updates);

    // Only update backend if we are toggling something, or moving an ENABLED handle
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

  setFFTWindow: (sec) => set({ fft_window: sec } as any),
  setOctaveShift: (shift) => set({ octave_shift: shift } as any),
});
