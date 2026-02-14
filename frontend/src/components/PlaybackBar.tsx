import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { Play, Pause, Square, Volume2, Settings, Timer, ChevronUp, ChevronDown } from 'lucide-react';
import { SettingsDialog } from './SettingsDialog';

export const PlaybackBar: React.FC = () => {
  const {
    loaded, position, duration, playing, speed, volume, filename,
    controlPlayback, browseFile, currentTheme, themes,
    metronome_enabled, updateMetronome, fft_window, setFFTWindow,
    octave_shift, setOctaveShift
  } = useStore();

  const [showSettings, setShowSettings] = useState(false);
  const theme = themes[currentTheme] || {};

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (position / duration) * 100 : 0;

  return (
    <div className="p-2 flex items-center gap-4 border-b select-none h-16 shrink-0" style={{ backgroundColor: theme.surface, color: theme.text }}>
      <div className="flex items-center gap-2">
        {loaded ? (
            <>
                <button onClick={() => controlPlayback(playing ? 'pause' : 'play')} className="p-2 hover:bg-white/10 rounded transition-colors">
                {playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
                </button>
                <button onClick={() => controlPlayback('stop')} className="p-2 hover:bg-white/10 rounded transition-colors">
                <Square size={20} fill="currentColor" />
                </button>
            </>
        ) : (
            <button onClick={browseFile} className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg active:scale-95 transition-all">Open Audio</button>
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
            <select value={fft_window} onChange={(e) => setFFTWindow(parseFloat(e.target.value))}
                    className="bg-transparent border border-white/10 rounded text-[10px] p-1 outline-none">
                <option value="0.1" className="bg-neutral-800">0.1s</option>
                <option value="0.3" className="bg-neutral-800">0.3s</option>
                <option value="0.5" className="bg-neutral-800">0.5s</option>
                <option value="1.0" className="bg-neutral-800">1.0s</option>
            </select>
        </div>

        {/* Octave Shift */}
        <div className="flex items-center gap-1 border-l border-white/10 pl-4 mr-2">
            <span className="text-[9px] opacity-60 font-bold mr-1">OCT</span>
            <button onClick={() => setOctaveShift(octave_shift - 1)} className="p-1 hover:bg-white/10 rounded"><ChevronDown size={14}/></button>
            <span className="text-[10px] font-mono w-4 text-center">{octave_shift > 0 ? `+${octave_shift}` : octave_shift}</span>
            <button onClick={() => setOctaveShift(octave_shift + 1)} className="p-1 hover:bg-white/10 rounded"><ChevronUp size={14}/></button>
        </div>

        {/* Speed & Volume */}
        <div className="flex items-center gap-2 border-l border-white/10 pl-4">
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

        <button onClick={() => setShowSettings(true)} className="p-2 hover:bg-white/10 rounded transition-colors" title="Settings">
            <Settings size={18} />
        </button>
      </div>

      {showSettings && <SettingsDialog onClose={() => setShowSettings(false)} />}
    </div>
  );
};
