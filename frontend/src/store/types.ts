export type ThemeName = string;

export interface Theme {
  name: string;
  surface: string;
  surfaceSecondary: string;
  text: string;
  accent: string;
  grid: string;
  playhead: string;
  flagRhythm: string;
  flagHarmony: string;
  keyWhite: string;
  keyBlack: string;
  spectrum: string;
}

export interface Flag {
  t: number;
  type: string;
  subdivision: number;
  name: string;
  auto_name?: string;
  is_section_start: boolean;
  shaded_subdivisions: boolean;
}

export interface Chord {
  root: string;
  accidental: string;
  quality: string;
  extension: string;
  alterations: string[];
  additions: string[];
  bass: string;
  bass_accidental: string;
}

export interface HarmonyFlag {
  t: number;
  chord: Chord;
}

export interface Lyric {
  text: string;
  timestamp: number;
  duration: number;
}

export interface TimeSignature {
  numerator: number;
  denominator: number;
}

export interface ExportStatus {
  active: boolean;
  progress: number;
  message: string;
}

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
  addLyric: (lyric: Lyric) => Promise<void>;
  removeLyric: (idx: number) => Promise<void>;
  updateLyric: (idx: number, lyric: Partial<Lyric>) => Promise<void>;
  moveLyric: (idx: number, t: number) => Promise<void>;
  updateTimeSignature: (numerator: number, denominator: number) => Promise<void>;
  saveProject: () => Promise<void>;
  exportMusicXML: () => Promise<void>;
  setEditingFlagIdx: (idx: number | null) => void;
  setEditingHarmonyFlagIdx: (idx: number | null) => void;
}

export interface PlaybackSlice {
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
  loop_mode: string;
  loop_range: [number, number];
  fft_window: number;
  octave_shift: number;

  controlPlayback: (action: string, value?: number) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  setLoopMode: (mode: string) => Promise<void>;
  playTone: (freq: number, action: 'start' | 'stop') => Promise<void>;
  stopAllTones: () => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;
}

export interface ConfigSlice {
  themes: Record<string, Theme>;
  currentTheme: string;
  metronome_enabled: boolean;
  click_volume: number;
  spectrum_keys: number;
  default_output_folder: string;
  musicxml_author: string;
  showSettings: boolean;
  showLyrics: boolean;

  // Filter settings also seem to be here sometimes
  filter_enabled: boolean;
  filter_low_enabled: boolean;
  filter_high_enabled: boolean;
  filter_low_hz: number;
  filter_high_hz: number;

  fetchThemes: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  setTheme: (name: string) => Promise<void>;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: any) => Promise<void>;
  setShowSettings: (show: boolean) => void;
  setShowLyrics: (show: boolean) => void;
  updateFilter: (filter: any) => Promise<void>;
}

export type AppState = ProjectSlice & PlaybackSlice & ConfigSlice;
