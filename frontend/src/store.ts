import { create } from 'zustand';

interface AppState {
  isPlaying: boolean;
  position: number;
  duration: number;
  speed: number;
  volume: number;
  waveform: number[];
  flags: any[];
  offset: number;
  zoom: number;
  setViewport: (offset: number, zoom: number) => void;
  setPlaying: (playing: boolean) => void;
  setPosition: (position: number) => void;
  setDuration: (duration: number) => void;
  setSpeed: (speed: number) => void;
  setVolume: (volume: number) => void;
  setWaveform: (waveform: number[]) => void;
  setFlags: (flags: any[]) => void;
}

export const useStore = create<AppState>((set) => ({
  isPlaying: false,
  position: 0,
  duration: 0,
  speed: 1.0,
  volume: 1.0,
  waveform: [],
  flags: [],
  offset: 0,
  zoom: 1,
  setViewport: (offset, zoom) => set({ offset, zoom }),
  setPlaying: (playing) => set({ isPlaying: playing }),
  setPosition: (position) => set({ position }),
  setDuration: (duration) => set({ duration }),
  setSpeed: (speed) => set({ speed }),
  setVolume: (volume) => set({ volume }),
  setWaveform: (waveform) => set({ waveform }),
  setFlags: (flags) => set({ flags }),
}));
