import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState, Chord, Lyric } from '../types';
import { API_BASE } from '../useStore';

export const createProjectSlice: StateCreator<AppState, [], [], any> = (set, get) => ({
  loaded: false,
  filename: '',
  metadata: { title: '', artist: '', album: '' },
  flags: [],
  harmony_flags: [],
  lyrics: [],
  time_signature: { numerator: 4, denominator: 4 },
  dirty: false,
  editingFlagIdx: null,
  editingHarmonyFlagIdx: null,
  export_status: { active: false, progress: 0, message: '' },

  fetchStatus: async () => {
    try {
      const res = await axios.get(`${API_BASE}/status`);
      set(res.data);
    } catch (e) {
      console.error("[Store] Failed to fetch status:", e);
    }
  },

  browseFile: async () => {
    try {
      const res = await axios.get(`${API_BASE}/browse`);
      if (res.data.status === 'loaded') {
          get().fetchStatus();
      }
    } catch (e) {
      console.error("[Store] Failed to browse:", e);
    }
  },

  addFlag: async (t: number) => {
    try {
        await axios.post(`${API_BASE}/project/flags`, { t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to add flag:", e);
    }
  },

  moveFlag: async (idx: number, t: number) => {
    try {
        await axios.post(`${API_BASE}/project/flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move flag:", e);
    }
  },

  removeFlag: async (idx: number) => {
    try {
        await axios.delete(`${API_BASE}/project/flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove flag:", e);
    }
  },

  addHarmonyFlag: async (t: number, chord?: Chord) => {
    try {
        if (!chord) {
            chord = await get().analyzeChord(t);
        }
        await axios.post(`${API_BASE}/project/harmony_flags`, { t, chord });
        get().fetchStatus();
        return { t, chord };
    } catch (e) {
        console.error("[Store] Failed to add harmony flag:", e);
        return null;
    }
  },

  moveHarmonyFlag: async (idx: number, t: number) => {
    try {
        await axios.post(`${API_BASE}/project/harmony_flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move harmony flag:", e);
    }
  },

  removeHarmonyFlag: async (idx: number) => {
    try {
        await axios.delete(`${API_BASE}/project/harmony_flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove harmony flag:", e);
    }
  },

  updateHarmonyFlag: async (idx: number, t: number, chord: Chord) => {
    try {
        await axios.patch(`${API_BASE}/project/harmony_flags/${idx}`, { t, chord });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to update harmony flag:", e);
    }
  },

  analyzeChord: async (t: number) => {
    try {
        const res = await axios.get(`${API_BASE}/project/analyze_chord`, { params: { t } });
        return res.data;
    } catch (e) {
        console.error("[Store] Failed to analyze chord:", e);
        return { root: 'C', accidental: '', quality: 'M', extension: '', alterations: [], additions: [], bass: '', bass_accidental: '' };
    }
  },

  addLyric: async (lyric: Lyric) => {
    try {
        await axios.post(`${API_BASE}/project/lyrics`, lyric);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to add lyric:", e);
    }
  },

  removeLyric: async (idx: number) => {
    try {
        await axios.delete(`${API_BASE}/project/lyrics/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove lyric:", e);
    }
  },

  updateLyric: async (idx: number, lyric: Partial<Lyric>) => {
    try {
        await axios.patch(`${API_BASE}/project/lyrics/${idx}`, lyric);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to update lyric:", e);
    }
  },

  moveLyric: async (idx: number, t: number) => {
    try {
        await axios.post(`${API_BASE}/project/lyrics/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move lyric:", e);
    }
  },

  updateTimeSignature: async (numerator: number, denominator: number) => {
    try {
        await axios.post(`${API_BASE}/project/time_signature`, { numerator, denominator });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to update time signature:", e);
    }
  },

  saveProject: async () => {
    try {
        await axios.post(`${API_BASE}/project/save`);
        set({ dirty: false });
    } catch (e) {
        console.error("[Store] Failed to save project:", e);
    }
  },

  exportMusicXML: async () => {
    try {
        // Simple mock for browser case in this context
        await axios.get(`${API_BASE}/project/export/musicxml`);
    } catch (e) {
        console.error("[Store] Failed to export MusicXML:", e);
    }
  },

  setEditingFlagIdx: (idx: number | null) => set({ editingFlagIdx: idx }),
  setEditingHarmonyFlagIdx: (idx: number | null) => set({ editingHarmonyFlagIdx: idx }),
});
