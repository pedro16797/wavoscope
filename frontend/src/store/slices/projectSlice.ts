import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState, Flag, HarmonyFlag, Chord, TimeSignature, ExportStatus, Lyric } from '../types';
import { API_BASE } from '../useStore';

export interface ProjectSlice {
  loaded: boolean;
  filename: string;
  metadata: {
    title: string;
    artist: string;
    album: string;
  };
  flags: Flag[];
  harmony_flags: HarmonyFlag[];
  lyrics: Lyric[];
  time_signature: TimeSignature;
  dirty: boolean;
  editingFlagIdx: number | null;
  editingHarmonyFlagIdx: number | null;
  export_status: ExportStatus;

  fetchStatus: () => Promise<void>;
  browseFile: () => Promise<void>;
  addFlag: (t: number) => Promise<void>;
  moveFlag: (idx: number, t: number) => Promise<void>;
  removeFlag: (idx: number) => Promise<void>;
  addHarmonyFlag: (t: number, chord?: Chord) => Promise<HarmonyFlag | null>;
  moveHarmonyFlag: (idx: number, t: number) => Promise<void>;
  removeHarmonyFlag: (idx: number) => Promise<void>;
  updateHarmonyFlag: (idx: number, t: number, chord: Chord) => Promise<void>;
  analyzeChord: (t: number) => Promise<Chord>;
  addLyric: (lyric: Lyric) => Promise<{ idx: number, lyric: Lyric } | null>;
  removeLyric: (idx: number) => Promise<void>;
  updateLyric: (idx: number, lyric: Partial<Lyric>) => Promise<{ idx: number, lyric: Lyric } | null>;
  moveLyric: (idx: number, t: number) => Promise<{ idx: number, lyric: Lyric } | null>;
  updateTimeSignature: (numerator: number, denominator: number) => Promise<void>;
  saveProject: () => Promise<void>;
  exportMusicXML: () => Promise<void>;
  setEditingFlagIdx: (idx: number | null) => void;
  setEditingHarmonyFlagIdx: (idx: number | null) => void;
}

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
        const res = await axios.get(`${API_BASE}/browse`);
        if (res.data.status !== 'loaded') return;
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
        await get().fetchStatus();
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
        return {
            root: 'C', accidental: '', quality: 'M', extension: '',
            alterations: [], additions: [], bass: '', bass_accidental: ''
        };
    }
  },

  addLyric: async (lyric: Lyric) => {
    try {
        const res = await axios.post(`${API_BASE}/project/lyrics`, lyric);
        get().fetchStatus();
        return { idx: res.data.idx, lyric: res.data.new_lyric };
    } catch (e) {
        console.error("[Store] Failed to add lyric:", e);
        return null;
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
        const res = await axios.patch(`${API_BASE}/project/lyrics/${idx}`, lyric);
        get().fetchStatus();
        return { idx: res.data.new_idx, lyric: res.data.updated_lyric };
    } catch (e) {
        console.error("[Store] Failed to update lyric:", e);
        return null;
    }
  },

  moveLyric: async (idx: number, t: number) => {
    try {
        const res = await axios.post(`${API_BASE}/project/lyrics/move`, { idx, t });
        get().fetchStatus();
        return { idx: res.data.new_idx, lyric: res.data.updated_lyric };
    } catch (e) {
        console.error("[Store] Failed to move lyric:", e);
        return null;
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
        const checkRes = await axios.get(`${API_BASE}/project/export/musicxml/check`);
        if (!checkRes.data.can_export) {
            alert(checkRes.data.reason || "Cannot export project.");
            return;
        }

        const defaultFilename = (get().filename || 'transcription').replace(/\.[^/.]+$/, "") + ".musicxml";
        let savePath: string | null = null;

        const pywindow = window as any;
        if (pywindow.pywebview?.api?.save_dialog) {
            const res = await pywindow.pywebview.api.save_dialog(defaultFilename, get().default_output_folder || null);
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
    if (idx === null && get().loop_mode === 'lyric') {
      get().setLoopMode('none');
    }
  },
});
