import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState, Chord, Lyric, Flag, ProjectSlice } from '../types';
import { API_BASE } from '../useStore';

export const createProjectSlice: StateCreator<AppState, [], [], ProjectSlice> = (set, get) => ({
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
  selectedLyricIdx: null,
  export_status: { active: false, progress: 0, message: '' },

  fetchStatus: async () => {
    try {
      const res = await axios.get(`${API_BASE}/status`);
      const { filter_low_hz, filter_high_hz, ...rest } = res.data;
      set(rest);
    } catch (e) {
      console.error("[Store] Failed to fetch status:", e);
    }
  },

  browseFile: async () => {
    const pywindow = window as any;
    try {
      if (pywindow.pywebview?.api?.browse) {
        await pywindow.pywebview.api.browse();
      } else {
        console.warn("[Store] browseFile fallback is not implemented in the backend.");
        return;
      }

      await get().fetchStatus();

      const state = get();
      await state.updateFilter({
          low_hz: state.filter_low_hz,
          high_hz: state.filter_high_hz,
          enabled: state.filter_enabled,
          low_enabled: state.filter_low_enabled,
          high_enabled: state.filter_high_enabled
      });
    } catch (e) {
      console.error("[Store] Failed to browse or load file:", e);
    }
  },

  addFlag: async (t: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/flags`, { t });
        set({ flags: res.data.flags });
        return { idx: res.data.idx };
    } catch (e) {
        console.error("[Store] Failed to add flag:", e);
        return null;
    }
  },

  moveFlag: async (idx: number, t: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/flags/move`, { idx, t });
        set({ flags: res.data.flags });
        return { idx: res.data.new_idx, flag: res.data.updated_flag };
    } catch (e) {
        console.error("[Store] Failed to move flag:", e);
        return null;
    }
  },

  removeFlag: async (idx: number) => {
    try {
        const res = await axios.delete(`${API_BASE}/project/flags/${idx}`);
        set({ flags: res.data.flags });
    } catch (e) {
        console.error("[Store] Failed to remove flag:", e);
    }
  },

  updateFlag: async (idx: number, flag: Partial<Flag>) => {
    try {
        const res = await axios.patch(`${API_BASE}/project/flags/${idx}`, flag);
        set({ flags: res.data.flags });
    } catch (e) {
        console.error("[Store] Failed to update flag:", e);
    }
  },

  insertNFlags: async (left_idx: number, count: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/flags/insert_n`, { left_idx, count });
        set({ flags: res.data.flags });
    } catch (e) {
        console.error("[Store] Failed to insert flags:", e);
    }
  },

  addHarmonyFlag: async (t: number, chord?: Chord) => {
    try {
        if (!chord) {
            chord = await get().analyzeChord(t);
        }
        const res = await axios.post(`${API_BASE}/project/harmony_flags`, { t, c: chord });
        set({ harmony_flags: res.data.harmony_flags });
        return { idx: res.data.idx, t, c: chord };
    } catch (e) {
        console.error("[Store] Failed to add harmony flag:", e);
        return null;
    }
  },

  moveHarmonyFlag: async (idx: number, t: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/harmony_flags/move`, { idx, t });
        set({ harmony_flags: res.data.harmony_flags });
        return { idx: res.data.new_idx, t: res.data.updated_flag.t, c: res.data.updated_flag.c };
    } catch (e) {
        console.error("[Store] Failed to move harmony flag:", e);
        return null;
    }
  },

  removeHarmonyFlag: async (idx: number) => {
    try {
        const res = await axios.delete(`${API_BASE}/project/harmony_flags/${idx}`);
        set({ harmony_flags: res.data.harmony_flags });
    } catch (e) {
        console.error("[Store] Failed to remove harmony flag:", e);
    }
  },

  updateHarmonyFlag: async (idx: number, t: number, chord: Chord) => {
    try {
        const res = await axios.patch(`${API_BASE}/project/harmony_flags/${idx}`, { t, c: chord });
        set({ harmony_flags: res.data.harmony_flags });
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
        return {
            r: 'C', ca: '', q: '', ext: '',
            alt: [], add: [], b: '', ba: ''
        };
    }
  },

  addLyric: async (lyric: Lyric) => {
    try {
        const res = await axios.post(`${API_BASE}/project/lyrics`, lyric);
        set({ lyrics: res.data.lyrics });
        return { idx: res.data.idx, lyric: res.data.new_lyric };
    } catch (e) {
        console.error("[Store] Failed to add lyric:", e);
        return null;
    }
  },

  removeLyric: async (idx: number) => {
    try {
        const res = await axios.delete(`${API_BASE}/project/lyrics/${idx}`);
        set({ lyrics: res.data.lyrics });
    } catch (e) {
        console.error("[Store] Failed to remove lyric:", e);
    }
  },

  updateLyric: async (idx: number, lyric: Partial<Lyric>) => {
    try {
        const res = await axios.patch(`${API_BASE}/project/lyrics/${idx}`, lyric);
        set({ lyrics: res.data.lyrics });
        return { idx: res.data.new_idx, lyric: res.data.updated_lyric };
    } catch (e) {
        console.error("[Store] Failed to update lyric:", e);
        return null;
    }
  },

  moveLyric: async (idx: number, t: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/lyrics/move`, { idx, t });
        set({ lyrics: res.data.lyrics });
        return { idx: res.data.new_idx, lyric: res.data.updated_lyric };
    } catch (e) {
        console.error("[Store] Failed to move lyric:", e);
        return null;
    }
  },

  updateTimeSignature: async (numerator: number, denominator: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/time_signature`, { numerator, denominator });
        set({ time_signature: res.data.time_signature });
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
        const checkRes = await axios.get(`${API_BASE}/project/export/musicxml/check`);
        if (!checkRes.data.can_export) {
            alert(checkRes.data.reason || "Cannot export project.");
            return;
        }

        const defaultFilename = (get().filename || 'transcription').replace(/\.[^/.]+$/, "") + ".musicxml";
        let savePath: string | null = null;

        const pywindow = window as any;
        if (pywindow.pywebview?.api?.save_dialog) {
            const res = await pywindow.pywebview.api.save_dialog(defaultFilename, get().default_output_folder || '');
            if (res) savePath = Array.isArray(res) ? res[0] : res;
        } else {
            set({ export_status: { active: true, progress: 0, message: 'Generating MusicXML...' } });
            try {
                const res = await axios.get(`${API_BASE}/project/export/musicxml`, { responseType: 'blob' });
                const url = window.URL.createObjectURL(res.data);
                const link = document.createElement('a');
                link.style.display = 'none'; link.href = url;
                link.setAttribute('download', defaultFilename);
                document.body.appendChild(link);
                link.click();
                setTimeout(() => { document.body.removeChild(link); window.URL.revokeObjectURL(url); }, 100);
                set({ export_status: { active: true, progress: 1.0, message: 'Done!' } });
                setTimeout(() => set({ export_status: { active: false, progress: 0, message: '' } }), 1000);
                return;
            } catch (e) {
                set({ export_status: { active: false, progress: 0, message: '' } });
                throw e;
            }
        }

        if (!savePath) return;
        await axios.post(`${API_BASE}/project/export/musicxml/start`, { path: savePath });

        const poll = async () => {
            try {
                const res = await axios.get(`${API_BASE}/project/export/musicxml/progress`);
                set({ export_status: res.data });
                if (res.data.active) setTimeout(poll, 200);
            } catch (e) {
                console.error("[Store] Progress poll failed:", e);
                set({ export_status: { active: false, progress: 0, message: '' } });
            }
        };
        poll();
    } catch (e) {
        console.error("[Store] Failed to export MusicXML:", e);
        set({ export_status: { active: false, progress: 0, message: '' } });
    }
  },

  setEditingFlagIdx: (idx: number | null) => set({ editingFlagIdx: idx }),
  setEditingHarmonyFlagIdx: (idx: number | null) => set({ editingHarmonyFlagIdx: idx }),
  setSelectedLyricIdx: (idx: number | null) => {
    set({ selectedLyricIdx: idx });
    axios.post(`${API_BASE}/project/lyrics/select`, { idx })
      .then(() => get().fetchStatus())
      .catch(e => console.error("[Store] Failed to sync lyric selection:", e));
    if (idx === null && get().loop_mode === 'lyric') {
      get().setLoopMode('none');
    }
  },
});
