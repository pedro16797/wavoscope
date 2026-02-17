export interface Flag {
  t: number;
  type: string;
  subdivision: number;
  name: string;
  is_section_start: boolean;
  shaded_subdivisions: boolean;
  auto_name?: string;
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

export interface TimeSignature {
  numerator: number;
  denominator: number;
}

export interface ExportStatus {
  active: boolean;
  progress: number;
  message: string;
}

export interface AppState {
  loaded: boolean;
  position: number;
  duration: number;
  playing: boolean;
  speed: number;
  volume: number;
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
  metronome_enabled: boolean;
  click_volume: number;
  loop_mode: string;
  loop_range: [number, number];
  filter_enabled: boolean;
  filter_low_enabled: boolean;
  filter_high_enabled: boolean;
  filter_low_hz: number;
  filter_high_hz: number;
  themes: Record<string, Record<string, string>>;
  currentTheme: string;
  spectrum_keys: number;
  high_quality_enhancement: boolean;
  default_output_folder: string;
  musicxml_author: string;
  fft_window: number;
  octave_shift: number;

  // UI State
  showSettings: boolean;
  editingFlagIdx: number | null;
  editingHarmonyFlagIdx: number | null;
  export_status: ExportStatus;

  fetchStatus: () => Promise<void>;
  fetchThemes: () => Promise<void>;
  fetchConfig: () => Promise<void>;
  controlPlayback: (action: string, value?: number) => Promise<void>;
  browseFile: () => Promise<void>;
  setTheme: (name: string) => Promise<void>;
  updatePosition: (pos: number) => void;
  setPlaying: (playing: boolean) => void;
  updateMetronome: (enabled?: boolean, gain?: number) => Promise<void>;
  updateConfig: (cfg: {
    theme?: string,
    click_volume?: number,
    spectrum_keys?: number,
    high_quality_enhancement?: boolean,
    default_output_folder?: string,
    musicxml_author?: string
  }) => Promise<void>;
  addFlag: (t: number) => Promise<void>;
  moveFlag: (idx: number, t: number) => Promise<void>;
  removeFlag: (idx: number) => Promise<void>;
  setLoopMode: (mode: string) => Promise<void>;
  updateFilter: (filter: { enabled?: boolean, low_hz?: number, high_hz?: number, low_enabled?: boolean, high_enabled?: boolean }) => Promise<void>;
  ensureFiltersVisible: () => void;

  addHarmonyFlag: (t: number, chord?: Chord) => Promise<HarmonyFlag | null>;
  moveHarmonyFlag: (idx: number, t: number) => Promise<void>;
  removeHarmonyFlag: (idx: number) => Promise<void>;
  updateHarmonyFlag: (idx: number, t: number, chord: Chord) => Promise<void>;
  analyzeChord: (t: number) => Promise<Chord>;

  updateTimeSignature: (numerator: number, denominator: number) => Promise<void>;
  saveProject: () => Promise<void>;
  exportMusicXML: () => Promise<void>;
  setFFTWindow: (sec: number) => void;
  setOctaveShift: (shift: number) => void;

  setShowSettings: (show: boolean) => void;
  setEditingFlagIdx: (idx: number | null) => void;
  setEditingHarmonyFlagIdx: (idx: number | null) => void;
}
