import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { Timeline } from './Timeline';
import { Waveform } from './Waveform';
import { LyricsTimeline } from './LyricsTimeline';
import { Type } from 'lucide-react';

export const WaveformView: React.FC = () => {
  const { showLyrics, setShowLyrics } = useStore();
  const [viewport, setViewport] = useState({ offset: 0, zoom: 100 });

  const handleViewportChange = (offset: number, zoom: number) => {
    setViewport({ offset, zoom });
  };

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="h-6 border-b-[width:var(--ui-border)] flex items-center justify-between px-4 font-bold text-[10px] opacity-50 uppercase tracking-widest shrink-0 bg-surface"
           style={{ borderBottomColor: 'var(--color-grid)' }}>
        <span>Timeline & Waveform</span>
        <button
          onClick={() => setShowLyrics(!showLyrics)}
          className={`flex items-center gap-1 px-1 rounded transition-colors ${showLyrics ? 'bg-accent text-white opacity-100' : 'hover:bg-white/10'}`}
          title="Toggle Lyrics Track"
        >
          <Type size={12} />
          <span>Lyrics</span>
        </button>
      </div>
      <Timeline offset={viewport.offset} zoom={viewport.zoom} onViewportChange={handleViewportChange} />
      {showLyrics && <LyricsTimeline offset={viewport.offset} zoom={viewport.zoom} />}
      <div className="flex-1 min-h-0">
        <Waveform offset={viewport.offset} zoom={viewport.zoom} onViewportChange={handleViewportChange} />
      </div>
    </div>
  );
};
