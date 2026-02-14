import React, { useState } from 'react';
import { Timeline } from './Timeline';
import { Waveform } from './Waveform';

export const WaveformView: React.FC = () => {
  const [viewport, setViewport] = useState({ offset: 0, zoom: 100 });

  const handleViewportChange = (offset: number, zoom: number) => {
    setViewport({ offset, zoom });
  };

  return (
    <div className="flex flex-col h-full w-full">
      <div className="h-6 border-b flex items-center px-4 font-bold text-[10px] opacity-50 uppercase tracking-widest"
           style={{ backgroundColor: 'var(--color-surface)', borderBottomColor: 'var(--color-grid)' }}>
        Timeline & Waveform
      </div>
      <Timeline offset={viewport.offset} zoom={viewport.zoom} />
      <div className="flex-1">
        <Waveform offset={viewport.offset} zoom={viewport.zoom} onViewportChange={handleViewportChange} />
      </div>
    </div>
  );
};
