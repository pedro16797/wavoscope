import type { StateCreator } from 'zustand';
import axios from 'axios';
import type { AppState, Flag, HarmonyFlag, Chord, TimeSignature, ExportStatus } from '../types';
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
  time_signature: { numerator: 4, denominator: 4 },
  dirty: false,
  editingFlagIdx: null,
  editingHarmonyFlagIdx: null,
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
    const pywindow = window as Window & { pywebview?: { api: { browse: () => Promise<void> } } };
    try {
      if (pywindow.pywebview?.api?.browse) {
        await pywindow.pywebview.api.browse();
      } else {
        const res = await axios.get(`${API_BASE}/browse`);
        if (res.data.status !== 'loaded') return;
      }

      await get().fetchStatus();

      // Sync filter to new backend
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

  addFlag: async (t) => {
    try {
        await axios.post(`${API_BASE}/project/flags`, { t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to add flag:", e);
    }
  },

  moveFlag: async (idx, t) => {
    try {
        await axios.post(`${API_BASE}/project/flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move flag:", e);
    }
  },

  removeFlag: async (idx) => {
    try {
        await axios.delete(`${API_BASE}/project/flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove flag:", e);
    }
  },

  addHarmonyFlag: async (t, chord) => {
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

  moveHarmonyFlag: async (idx, t) => {
    try {
        await axios.post(`${API_BASE}/project/harmony_flags/move`, { idx, t });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to move harmony flag:", e);
    }
  },

  removeHarmonyFlag: async (idx) => {
    try {
        await axios.delete(`${API_BASE}/project/harmony_flags/${idx}`);
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to remove harmony flag:", e);
    }
  },

  updateHarmonyFlag: async (idx, t, chord) => {
    try {
        await axios.patch(`${API_BASE}/project/harmony_flags/${idx}`, { t, chord });
        get().fetchStatus();
    } catch (e) {
        console.error("[Store] Failed to update harmony flag:", e);
    }
  },

  analyzeChord: async (t) => {
    try {
        const res = await axios.get(`${API_BASE}/project/analyze_chord`, { params: { t } });
        return res.data;
    } catch (e) {
        console.error("[Store] Failed to analyze chord:", e);
        return {
            root: 'C',
            accidental: '',
            quality: 'M',
            extension: '',
            alterations: [],
            additions: [],
            bass: '',
            bass_accidental: ''
        };
    }
  },

  updateTimeSignature: async (numerator, denominator) => {
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
        // 1. Check if export is possible
        const checkRes = await axios.get(`${API_BASE}/project/export/musicxml/check`);
        if (!checkRes.data.can_export) {
            alert(checkRes.data.reason || "Cannot export project.");
            return;
        }

        const defaultFilename = (get().filename || 'transcription').replace(/\.[^/.]+$/, "") + ".musicxml";
        let savePath: string | null = null;

        // 2. Prompt for save location
        const pywindow = window as any;
        if (pywindow.pywebview?.api?.save_dialog) {
            const defaultDir = get().default_output_folder || null;
            const res = await pywindow.pywebview.api.save_dialog(defaultFilename, defaultDir);
            if (res) {
                savePath = Array.isArray(res) ? res[0] : res;
            }
        } else {
            // Fallback for browser: direct download (old way)
            // But user wants a progress bar. We'll show an indeterminate one for browser case.
            set({ export_status: { active: true, progress: 0, message: 'Generating MusicXML...' } });
            try {
                const res = await axios.get(`${API_BASE}/project/export/musicxml`, { responseType: 'blob' });
                const url = window.URL.createObjectURL(res.data);
                const link = document.createElement('a');
                link.style.display = 'none';
                link.href = url;
                link.setAttribute('download', defaultFilename);
                document.body.appendChild(link);
                link.click();
                setTimeout(() => {
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                }, 100);
                set({ export_status: { active: true, progress: 1.0, message: 'Done!' } });
                setTimeout(() => set({ export_status: { active: false, progress: 0, message: '' } }), 1000);
                return;
            } catch (e) {
                set({ export_status: { active: false, progress: 0, message: '' } });
                throw e;
            }
        }

        if (!savePath) return; // User cancelled

        // 3. Start export task
        await axios.post(`${API_BASE}/project/export/musicxml/start`, { path: savePath });

        // 4. Poll for progress
        const poll = async () => {
            try {
                const res = await axios.get(`${API_BASE}/project/export/musicxml/progress`);
                set({ export_status: res.data });
                if (res.data.active) {
                    setTimeout(poll, 200);
                }
            } catch (e) {
                console.error("[Store] Progress poll failed:", e);
                set({ export_status: { active: false, progress: 0, message: '' } });
            }
        };
        poll();

    } catch (e) {
        console.error("[Store] Failed to export MusicXML:", e);
        alert("Failed to export MusicXML. Please check the backend console.");
        set({ export_status: { active: false, progress: 0, message: '' } });
    }
  },

  setEditingFlagIdx: (idx) => set({ editingFlagIdx: idx }),
  setEditingHarmonyFlagIdx: (idx) => set({ editingHarmonyFlagIdx: idx }),
});
