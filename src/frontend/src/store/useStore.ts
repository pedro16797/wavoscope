import { create } from 'zustand';
import type { AppState } from './types';
import { createPlaybackSlice } from './slices/playbackSlice';
import { createProjectSlice } from './slices/projectSlice';
import { createConfigSlice } from './slices/configSlice';
import { createPlaylistSlice } from './slices/playlistSlice';

// Re-exported for backwards compatibility; the source of truth is src/env.ts.
export { API_BASE } from '../env';

export const useStore = create<AppState>((...a) => ({
  ...createPlaybackSlice(...a),
  ...createProjectSlice(...a),
  ...createConfigSlice(...a),
  ...createPlaylistSlice(...a),
}));
