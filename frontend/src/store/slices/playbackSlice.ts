import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState } from '../types';
import { API_BASE } from '../useStore';

export const createPlaybackSlice: StateCreator<AppState, [], [], any> = (set, get) => ({
  position: 0,
  duration: 0,
  playing: false,
  speed: 1.0,
  volume: 1.0,
  loop_mode: 'none',
  loop_range: [0, 0],
  fft_window: 0.3,
  octave_shift: 0,

  controlPlayback: async (action: string, value?: number) => {
    try {
      await axios.post(`${API_BASE}/playback`, { action, value });
      if (action === 'set_speed' && value !== undefined) set({ speed: value });
      if (action === 'set_volume' && value !== undefined) set({ volume: value });
      if (action === 'play') set({ playing: true });
      if (action === 'pause' || action === 'stop') set({ playing: false });
    } catch (e) {
      console.error(`[Store] Failed to control playback (${action}):`, e);
    }
  },

  updatePosition: (pos: number) => set({ position: pos }),
  setPlaying: (playing: boolean) => set({ playing }),
  setLoopMode: async (mode: string) => {
    try {
        await axios.post(`${API_BASE}/playback/loop`, { mode });
        set({ loop_mode: mode });
    } catch (e) {
        console.error("[Store] Failed to set loop mode:", e);
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
  setOctaveShift: (shift: number) => set({ octave_shift: shift }),
});
