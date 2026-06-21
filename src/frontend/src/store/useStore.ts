import { create } from 'zustand';
import axios from 'axios';
import type { AppState } from './types';
import { createPlaybackSlice } from './slices/playbackSlice';
import { createProjectSlice } from './slices/projectSlice';
import { createConfigSlice } from './slices/configSlice';
import { createPlaylistSlice } from './slices/playlistSlice';
import { REMOTE_TOKEN } from '../env';

// Re-exported for backwards compatibility; the source of truth is src/env.ts.
export { API_BASE } from '../env';

// Authorize remote devices on every request. Empty (and thus unset) on the
// host's own loopback browser, which is authorized without a token.
if (REMOTE_TOKEN) {
  axios.defaults.headers.common['X-Wavoscope-Token'] = REMOTE_TOKEN;
}

export const useStore = create<AppState>((...a) => ({
  ...createPlaybackSlice(...a),
  ...createProjectSlice(...a),
  ...createConfigSlice(...a),
  ...createPlaylistSlice(...a),
}));
