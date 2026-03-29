import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState, PlaylistSlice, PlaylistItem } from '../types';
import { API_BASE } from '../useStore';

export const createPlaylistSlice: StateCreator<AppState, [], [], PlaylistSlice> = (set, get) => ({
    playlists: [],
    activePlaylistId: null,
    activeItemId: null,
    showPlaylistDialog: false,

    fetchPlaylists: async () => {
        try {
            const res = await axios.get(`${API_BASE}/playlists`);
            const activeRes = await axios.get(`${API_BASE}/playlists/active`);
            set({
                playlists: res.data,
                activePlaylistId: activeRes.data.active_playlist_id,
                activeItemId: activeRes.data.active_item_id
            });
        } catch (e) {
            console.error("[Store] Failed to fetch playlists:", e);
        }
    },

    createPlaylist: async (name: string) => {
        try {
            await axios.post(`${API_BASE}/playlists`, { name });
            await get().fetchPlaylists();
        } catch (e) {
            console.error("[Store] Failed to create playlist:", e);
        }
    },

    updatePlaylist: async (id: string, name: string) => {
        try {
            await axios.patch(`${API_BASE}/playlists/${id}`, { name });
            await get().fetchPlaylists();
        } catch (e) {
            console.error("[Store] Failed to update playlist:", e);
        }
    },

    deletePlaylist: async (id: string) => {
        try {
            await axios.delete(`${API_BASE}/playlists/${id}`);
            await get().fetchPlaylists();
        } catch (e) {
            console.error("[Store] Failed to delete playlist:", e);
        }
    },

    addItemToPlaylist: async (playlistId: string, path: string, name?: string) => {
        try {
            await axios.post(`${API_BASE}/playlists/${playlistId}/items`, { path, name });
            await get().fetchPlaylists();
        } catch (e) {
            console.error("[Store] Failed to add item to playlist:", e);
        }
    },

    removeItemFromPlaylist: async (playlistId: string, itemId: string) => {
        try {
            await axios.delete(`${API_BASE}/playlists/${playlistId}/items/${itemId}`);
            await get().fetchPlaylists();
        } catch (e) {
            console.error("[Store] Failed to remove item from playlist:", e);
        }
    },

    selectPlaylistItem: async (playlistId: string | null, itemId: string | null) => {
        try {
            await axios.post(`${API_BASE}/playlists/select`, null, { params: { playlist_id: playlistId, item_id: itemId } });
            set({ activePlaylistId: playlistId, activeItemId: itemId });
        } catch (e) {
            console.error("[Store] Failed to select playlist item:", e);
        }
    },

    loadPlaylistItem: async (item: PlaylistItem) => {
        try {
            await axios.post(`${API_BASE}/project/open`, { path: item.path });
            await get().fetchStatus();
            set({ activeItemId: item.id });
        } catch (e) {
            console.error("[Store] Failed to load playlist item:", e);
        }
    },

    setShowPlaylistDialog: (show: boolean) => set({ showPlaylistDialog: show }),

    nextPlaylistItem: async () => {
        try {
            await axios.post(`${API_BASE}/playback`, { action: 'next' });
            await get().fetchStatus();
            const activeRes = await axios.get(`${API_BASE}/playlists/active`);
            set({ activeItemId: activeRes.data.active_item_id });
        } catch (e) {
            console.error("[Store] Failed to navigate to next playlist item:", e);
        }
    },

    prevPlaylistItem: async () => {
        try {
            await axios.post(`${API_BASE}/playback`, { action: 'prev' });
            await get().fetchStatus();
            const activeRes = await axios.get(`${API_BASE}/playlists/active`);
            set({ activeItemId: activeRes.data.active_item_id });
        } catch (e) {
            console.error("[Store] Failed to navigate to previous playlist item:", e);
        }
    }
});
