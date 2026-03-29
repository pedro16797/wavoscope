import { create } from 'zustand';
import type { AppState } from './types';
import { createPlaybackSlice } from './slices/playbackSlice';
import { createProjectSlice } from './slices/projectSlice';
import { createConfigSlice } from './slices/configSlice';
import { createPlaylistSlice } from './slices/playlistSlice';

export const API_BASE = window.location.origin.includes(':5173') ? 'http://127.0.0.1:8000' : '';

export const useStore = create<AppState>((...a) => ({
  ...createPlaybackSlice(...a),
  ...createProjectSlice(...a),
  ...createConfigSlice(...a),
  ...createPlaylistSlice(...a),
}));
