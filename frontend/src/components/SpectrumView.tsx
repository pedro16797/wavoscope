import React from 'react';
import { useStore } from '../store/useStore';
import { ChevronUp, ChevronDown } from 'lucide-react';
import { Spectrum } from './Spectrum';
import { Tooltip } from './Tooltip';

export const SpectrumView: React.FC = () => {
  const {
    fft_window, setFFTWindow, octave_shift, setOctaveShift
  } = useStore();

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="h-6 border-b-[width:var(--ui-border)] flex items-center px-4 font-bold text-[10px] uppercase tracking-widest shrink-0 bg-surface justify-between"
           style={{ borderBottomColor: 'var(--color-grid)' }}>
        <span className="opacity-50">Spectrum Analyzer</span>

        <div className="flex items-center gap-4 h-full">
            {/* FFT Window */}
            <div className="flex items-center gap-2 h-full border-l border-white/10 pl-4">
                <span className="text-[9px] opacity-60 font-bold">FFT</span>
                <Tooltip content={`FFT Window: ${fft_window}s`}>
                    <input type="range" min="0.05" max="1.0" step="0.05" value={fft_window}
                        onChange={(e) => setFFTWindow(parseFloat(e.target.value))}
                        className="w-32 accent-current" />
                </Tooltip>
                <span className="text-[10px] font-mono w-8">{fft_window.toFixed(2)}s</span>
            </div>

            {/* Octave Shift */}
            <div className="flex items-center gap-1 h-full border-l-[width:var(--ui-border)] border-white/10 pl-4">
                <span className="text-[9px] opacity-60 font-bold mr-1">OCT</span>
                <button onClick={() => setOctaveShift(octave_shift - 1)} className="p-0.5 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronDown size={12}/></button>
                <span className="text-[10px] font-mono w-4 text-center">{octave_shift > 0 ? `+${octave_shift}` : octave_shift}</span>
                <button onClick={() => setOctaveShift(octave_shift + 1)} className="p-0.5 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronUp size={12}/></button>
            </div>
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <Spectrum />
      </div>
    </div>
  );
};
