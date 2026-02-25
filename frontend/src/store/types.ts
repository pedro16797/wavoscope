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
  waveform: string;
  background: string;
  radius: string;
  font: string;
  borderWidth: string;
}

export interface Flag {
  t: number;
  type: string;
  div: number;
  n: string;
  auto_name?: string;
  s: boolean;
  divshade: boolean;
}

export interface Chord {
  r: string;
  ca: string;
  q: string;
  ext: string;
  alt: string[];
  add: string[];
  b: string;
  ba: string;
}

export interface HarmonyFlag {
  t: number;
  c: Chord;
}

export interface Lyric {
  s: string;
  t: number;
  l: number;
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

export interface UndoStep {
  label: string;
  timestamp: number;
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
  editingFlagIdx: null | number;
  editingHarmonyFlagIdx: null | number;
  selectedLyricIdx: null | number;
  export_status: ExportStatus;
  undo_history: UndoStep[];

  fetchStatus: () => Promise<void>;
  browseFile: () => Promise<void>;
  addFlag: (t: number) => Promise<{ idx: number } | null>;
  moveFlag: (idx: number, t: number) => Promise<{ idx: number, flag: Flag } | null>;
  removeFlag: (idx: number) => Promise<void>;
  updateFlag: (idx: number, flag: Partial<Flag>) => Promise<void>;
  insertNFlags: (idx: number, count: number) => Promise<void>;
  addHarmonyFlag: (t: number, chord?: Chord) => Promise<{ idx: number, t: number, c: Chord } | null>;
  moveHarmonyFlag: (idx: number, t: number) => Promise<{ idx: number, t: number, c: Chord } | null>;
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
  setSelectedLyricIdx: (idx: number | null) => void;
  fetchUndoSteps: () => Promise<void>;
  restoreUndoStep: (index: number) => Promise<void>;
  undo: () => Promise<void>;
}

export interface PlaybackSlice {
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
  loop_mode: string;
  loop_range: [number, number];
  filter_enabled: boolean;
  filter_low_enabled: boolean;
  filter_high_enabled: boolean;
  filter_low_hz: number;
  filter_high_hz: number;
  fft_window: number;
  octave_shift: number;

  controlPlayback: (action: string, value?: number) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  setLoopMode: (mode: string) => Promise<void>;
  cycleLoopMode: () => Promise<void>;
  updateFilter: (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean }) => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;
  playTone: (freq: number, action: 'start' | 'stop') => Promise<void>;
  stopAllTones: () => Promise<void>;
}

export interface Locale {
  code: string;
  name: string;
}

export interface AudioDevice {
  index: number;
  name: string;
  hostapi: number;
  is_default: boolean;
}

export interface ConfigSlice {
  themes: Record<string, Theme>;
  currentTheme: ThemeName;
  locales: Locale[];
  audioDevices: AudioDevice[];
  metronome_enabled: boolean;
  click_volume: number;
  spectrum_keys: number;
  default_output_folder: string;
  musicxml_author: string;
  audio_device: string;
  autosave_enabled: boolean;
  autosave_forced: boolean;
  autosave_interval: number;
  autosave_max_snapshots: number;
  autosave_path: string;
  undo_steps: number;
  language: string;
  showSettings: boolean;
  showSpectrum: boolean;
  showLyrics: boolean;
  offset: number;
  zoom: number;

  fetchThemes: () => Promise<void>;
  fetchLocales: () => Promise<void>;
  fetchAudioDevices: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  setTheme: (name: ThemeName) => Promise<void>;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: {
    theme?: string,
    click_volume?: number,
    spectrum_keys?: number,
    default_output_folder?: string,
    musicxml_author?: string,
    audio_device?: string,
    autosave_enabled?: boolean,
    autosave_forced?: boolean,
    autosave_interval?: number,
    autosave_max_snapshots?: number,
    autosave_path?: string,
    undo_steps?: number,
    language?: string
  }) => Promise<void>;
  browseFolder: (initialDir?: string) => Promise<string | null>;
  setShowSettings: (show: boolean) => void;
  setShowSpectrum: (show: boolean) => void;
  setShowLyrics: (show: boolean) => void;
  setViewport: (offset: number, zoom: number) => void;
}

export type AppState = ProjectSlice & PlaybackSlice & ConfigSlice;
