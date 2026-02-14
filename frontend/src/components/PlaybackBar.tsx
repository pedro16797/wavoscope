import React from 'react';
import { useStore } from '../store/useStore';
import { Play, Pause, Square, Volume2 } from 'lucide-react';

export const PlaybackBar: React.FC = () => {
  const { loaded, position, duration, playing, speed, volume, filename, controlPlayback, browseFile, currentTheme, themes, setTheme } = useStore();
  const theme = themes[currentTheme] || {};

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!loaded) {
    return (
      <div className="p-4 flex items-center justify-between border-b" style={{ backgroundColor: theme.surface || '#252525', color: theme.text || '#fff' }}>
        <button onClick={browseFile} className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm">Open Audio File</button>
        <div className="text-sm opacity-50 italic">No audio loaded</div>
        <select value={currentTheme} onChange={(e) => setTheme(e.target.value)}
                className="bg-transparent border border-white/20 rounded text-[10px] p-1">
            {Object.keys(themes).map(t => <option key={t} value={t} className="bg-neutral-800">{t}</option>)}
        </select>
      </div>
    );
  }

  return (
    <div className="p-2 flex items-center gap-4 border-b select-none h-14" style={{ backgroundColor: theme.surface, color: theme.text }}>
      <div className="flex items-center gap-1">
        <button onClick={() => controlPlayback(playing ? 'pause' : 'play')} className="p-2 hover:bg-white/10 rounded transition-colors">
          {playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
        </button>
        <button onClick={() => controlPlayback('stop')} className="p-2 hover:bg-white/10 rounded transition-colors">
          <Square size={20} fill="currentColor" />
        </button>
      </div>

      <div className="flex-1 flex flex-col justify-center gap-1 min-w-0">
        <div className="text-xs font-bold truncate opacity-80">{filename}</div>
        <div className="flex items-center gap-2 text-[10px] font-mono">
            <span className="w-10 text-right">{formatTime(position)}</span>
            <div className="flex-1 h-1.5 bg-white/10 rounded-full relative overflow-hidden">
                <div className="absolute h-full rounded-full transition-all duration-75" style={{ width: `${(position/duration)*100}%`, backgroundColor: theme.accent }} />
            </div>
            <span className="w-10">{formatTime(duration)}</span>
        </div>
      </div>

      <div className="flex items-center gap-6 pr-2">
        <div className="flex items-center gap-2">
            <span className="text-[10px] opacity-60 font-bold">SPEED</span>
            <input type="range" min="0.1" max="2" step="0.1" value={speed}
                   onChange={(e) => controlPlayback('set_speed', parseFloat(e.target.value))}
                   className="w-20 accent-current" />
            <span className="text-[10px] font-mono w-8">{speed.toFixed(1)}x</span>
        </div>
        <div className="flex items-center gap-2">
            <Volume2 size={16} className="opacity-60" />
            <input type="range" min="0" max="1" step="0.05" value={volume}
                   onChange={(e) => controlPlayback('set_volume', parseFloat(e.target.value))}
                   className="w-16 accent-current" />
        </div>
        <select value={currentTheme} onChange={(e) => setTheme(e.target.value)}
                className="bg-transparent border border-white/10 rounded text-[10px] p-1 outline-none">
            {Object.keys(themes).map(t => <option key={t} value={t} className="bg-neutral-800">{t}</option>)}
        </select>
      </div>
    </div>
  );
};
