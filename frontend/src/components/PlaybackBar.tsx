import React from 'react';
import { useStore } from '../store/useStore';
import { Play, Pause, Square, Volume2, Settings, Timer, ChevronUp, ChevronDown, FolderOpen, Save, Repeat, Repeat1 } from 'lucide-react';

export const PlaybackBar: React.FC = () => {
  const {
    loaded, position, duration, playing, speed, volume, filename,
    controlPlayback, currentTheme, themes,
    metronome_enabled, updateMetronome, fft_window, setFFTWindow,
    octave_shift, setOctaveShift, setShowSettings, browseFile,
    saveProject, dirty, loop_mode, setLoopMode
  } = useStore();

  const theme = themes[currentTheme] || {};

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (position / duration) * 100 : 0;

  const cycleLoopMode = () => {
    const modes = ['none', 'whole', 'section', 'bar'];
    const nextIdx = (modes.indexOf(loop_mode) + 1) % modes.length;
    setLoopMode(modes[nextIdx]);
  };

  const getLoopIcon = () => {
    if (loop_mode === 'bar') return <Repeat1 size={20} />;
    return <Repeat size={20} />;
  };

  const getLoopTitle = () => {
    switch (loop_mode) {
        case 'whole': return 'Loop: Whole Song';
        case 'section': return 'Loop: Current Section';
        case 'bar': return 'Loop: Current Bar';
        default: return 'Loop: Off';
    }
  };

  return (
    <div className="p-2 flex items-center gap-4 border-b-[width:var(--ui-border)] select-none h-16 shrink-0 bg-surface" style={{ color: theme.text }}>
      <div className="flex items-center gap-1">
        <button onClick={browseFile} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors" title="Open Audio File">
            <FolderOpen size={20} />
        </button>
        <button onClick={saveProject} disabled={!loaded}
                className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors mr-2 ${!loaded ? 'opacity-20' : 'opacity-90'}`}
                title={dirty ? "Save Project (Unsaved changes)" : "Save Project"}>
            <Save size={20} className={dirty ? 'text-accent' : 'text-text'} />
        </button>
        {loaded && (
            <>
                <button onClick={() => controlPlayback(playing ? 'pause' : 'play')} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors">
                {playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
                </button>
                <button onClick={() => controlPlayback('stop')} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors mr-1">
                <Square size={20} fill="currentColor" />
                </button>
                <button onClick={cycleLoopMode}
                        className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors relative ${loop_mode !== 'none' ? 'text-accent' : 'opacity-40'}`}
                        title={getLoopTitle()}>
                    {getLoopIcon()}
                    {loop_mode === 'section' && <span className="absolute top-1 right-1 text-[8px] font-bold bg-accent text-surface rounded-full w-3 h-3 flex items-center justify-center border border-surface shadow-sm">S</span>}
                </button>
            </>
        )}
      </div>

      <div className="flex-1 flex flex-col justify-center gap-1 min-w-0 px-4">
        <div className="text-xs font-bold truncate opacity-80">{loaded ? filename : 'Ready to load audio'}</div>
        <div className="flex items-center gap-3 text-[11px] font-mono">
            <span className="w-12 text-right">{formatTime(position)}</span>
            <div className="flex-1 h-3 bg-white/5 rounded-full relative overflow-hidden cursor-pointer hover:bg-white/10 transition-colors shadow-inner border border-white/5"
                 onClick={(e) => {
                    if (!loaded || !duration) return;
                    const rect = e.currentTarget.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const seekT = (x / rect.width) * duration;
                    controlPlayback('seek', seekT);
                 }}>
                <div className="absolute h-full rounded-full transition-all duration-75" style={{ width: `${progressPercent}%`, backgroundColor: theme.accent }} />
            </div>
            <span className="w-10">{formatTime(duration)}</span>
        </div>
      </div>

      <div className="flex items-center gap-4 pr-2">
        {/* Metronome */}
        <button onClick={() => updateMetronome(!metronome_enabled)}
                className={`p-2 rounded transition-colors ${metronome_enabled ? 'text-accent bg-accent/10' : 'opacity-40'}`}
                title="Toggle Metronome">
            <Timer size={18} />
        </button>

        {/* FFT Window */}
        <div className="flex items-center gap-2 border-l border-white/10 pl-4">
            <span className="text-[9px] opacity-60 font-bold">FFT</span>
            <input type="range" min="0.05" max="1.0" step="0.05" value={fft_window}
                   onChange={(e) => setFFTWindow(parseFloat(e.target.value))}
                   className="w-16 accent-current" title={`FFT Window: ${fft_window}s`} />
            <span className="text-[10px] font-mono w-8">{fft_window.toFixed(2)}s</span>
        </div>

        {/* Octave Shift */}
        <div className="flex items-center gap-1 border-l-[width:var(--ui-border)] border-white/10 pl-4 mr-2">
            <span className="text-[9px] opacity-60 font-bold mr-1">OCT</span>
            <button onClick={() => setOctaveShift(octave_shift - 1)} className="p-1 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronDown size={14}/></button>
            <span className="text-[10px] font-mono w-4 text-center">{octave_shift > 0 ? `+${octave_shift}` : octave_shift}</span>
            <button onClick={() => setOctaveShift(octave_shift + 1)} className="p-1 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronUp size={14}/></button>
        </div>

        {/* Speed & Volume */}
        <div className="flex items-center gap-2 border-l-[width:var(--ui-border)] border-white/10 pl-4">
            <span className="text-[9px] opacity-60 font-bold">SPEED</span>
            <input type="range" min="0.1" max="2" step="0.1" value={speed}
                   onChange={(e) => controlPlayback('set_speed', parseFloat(e.target.value))}
                   className="w-16 accent-current" />
            <span className="text-[10px] font-mono w-8">{speed.toFixed(1)}x</span>
        </div>
        <div className="flex items-center gap-2">
            <Volume2 size={16} className="opacity-60" />
            <input type="range" min="0" max="1" step="0.05" value={volume}
                   onChange={(e) => controlPlayback('set_volume', parseFloat(e.target.value))}
                   className="w-16 accent-current" />
        </div>

        <button onClick={() => setShowSettings(true)} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors" title="Settings">
            <Settings size={18} />
        </button>
      </div>
    </div>
  );
};
