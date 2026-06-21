import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';
import { midiToFreq, maxOctaveShift, recomputeFilterHz, filterPayload } from '../utils';

import type { PlaybackSlice } from '../types';

// Coalesce filter POSTs: while one is in flight, dragging a cutoff handle would
// otherwise fire one request per mousemove. Mark "pending" instead and send the
// latest state once the in-flight request returns (~one request per round-trip).
let _filterInFlight = false;
let _filterPending = false;

async function _flushFilter(getState: () => AppState): Promise<void> {
  if (_filterInFlight) {
    _filterPending = true;
    return;
  }
  _filterInFlight = true;
  try {
    await axios.post(`${API_BASE}/playback/filter`, filterPayload(getState()));
  } catch (e) {
    console.error("[Store] Failed to update filter:", e);
  } finally {
    _filterInFlight = false;
    if (_filterPending) {
      _filterPending = false;
      _flushFilter(getState);
    }
  }
}

export const createPlaybackSlice: StateCreator<AppState, [], [], PlaybackSlice> = (set, get) => ({
  position: 0,
  duration: 0,
  playing: false,
  speed: 1.0,
  volume: 1.0,
  overdrive: false,
  normalVolume: 1.0,
  overdriveVolume: 1.0,
  loop_mode: 'none',
  loop_range: [0, 0],
  filter_enabled: true,
  filter_low_enabled: false,
  filter_high_enabled: false,
  filter_low_hz: midiToFreq(48 + 37 * 0.1),
  filter_high_hz: midiToFreq(48 + 37 * 0.9),
  filter_auto_gain: true,
  fft_window: 0.3,
  octave_shift: 0,

  controlPlayback: async (action: string, value?: number) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value });
      if (action === 'set_volume' && value !== undefined) {
          const updates: any = { volume: value };
          if (get().overdrive) {
              updates.overdriveVolume = value;
          } else {
              updates.normalVolume = value;
          }
          set(updates);
      }
    } catch (e) {
      console.error(`[Store] Failed to control playback (${action}):`, e);
    }
  },

  updatePosition: (pos: number, loop_range?: [number, number]) => {
    const updates: any = { position: pos };
    if (loop_range) updates.loop_range = loop_range;
    set(updates);
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
    const modes = ['none', 'lyric', 'section', 'bar', 'playlist', 'whole'];

    const isAvailable = (mode: string) => {
        if (mode === 'none' || mode === 'whole') return true;
        if (mode === 'lyric') return state.lyrics.length > 0;
        if (mode === 'section') return state.flags.some(f => f.s);
        if (mode === 'bar') return state.flags.some(f => f.type === 'rhythm');
        if (mode === 'playlist') return !!state.activePlaylistId;
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

  toggleOverdrive: async () => {
    const state = get();
    const newOverdrive = !state.overdrive;
    const newVolume = newOverdrive ? state.overdriveVolume : state.normalVolume;

    set({ overdrive: newOverdrive, volume: newVolume });
    try {
        await axios.post(`${API_BASE}/playback`, { action: 'set_volume', value: newVolume });
    } catch (e) {
        console.error("[Store] Failed to sync volume after overdrive toggle:", e);
    }
  },

  updateFilter: async (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean, auto_gain?: boolean }) => {
    const oldState = get();
    const updates: any = {};

    if (filter.enabled !== undefined) updates.filter_enabled = filter.enabled;
    if (filter.low_hz !== undefined) updates.filter_low_hz = filter.low_hz;
    if (filter.high_hz !== undefined) updates.filter_high_hz = filter.high_hz;
    if (filter.low_enabled !== undefined) updates.filter_low_enabled = filter.low_enabled;
    if (filter.high_enabled !== undefined) updates.filter_high_enabled = filter.high_enabled;
    if (filter.auto_gain !== undefined) updates.filter_auto_gain = filter.auto_gain;
    set(updates);

    const shouldUpdateBackend =
        filter.low_enabled !== undefined ||
        filter.high_enabled !== undefined ||
        filter.enabled !== undefined ||
        filter.auto_gain !== undefined ||
        (filter.low_hz !== undefined && oldState.filter_low_enabled) ||
        (filter.high_hz !== undefined && oldState.filter_high_enabled);

    if (shouldUpdateBackend) {
        // Coalesced: rapid drag updates collapse to roughly one request per
        // round-trip, and the final value is always sent.
        await _flushFilter(get);
    }
  },

  playTone: async (freq: number | number[], action: 'start' | 'stop', stopOthers: boolean = false) => {
    try {
        const payload: any = { action, stop_others: stopOthers };
        if (Array.isArray(freq)) {
            payload.freqs = freq;
        } else {
            payload.freq = freq;
        }
        await axios.post(`${API_BASE}/playback/tone`, payload);
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
    const clampedShift = Math.max(-2, Math.min(maxOctaveShift(state.spectrum_keys), shift));
    const oldShift = state.octave_shift;
    if (clampedShift === oldShift) return;

    const updates: any = {
        octave_shift: clampedShift,
        ...recomputeFilterHz(state.filter_low_hz, state.filter_high_hz,
            state.spectrum_keys, oldShift, state.spectrum_keys, clampedShift),
    };

    set(updates);

    if ((state.filter_low_enabled && updates.filter_low_hz) || (state.filter_high_enabled && updates.filter_high_hz)) {
        axios.post(`${API_BASE}/playback/filter`, filterPayload(get()))
            .catch(e => console.error("[Store] Failed to update filter after octave shift:", e));
    }
  },
});
