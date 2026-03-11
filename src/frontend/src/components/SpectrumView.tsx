import React from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { ChevronUp, ChevronDown } from 'lucide-react';
import { Spectrum } from './Spectrum';
import { Tooltip } from './Tooltip';

export const SpectrumView: React.FC = () => {
  const { t } = useTranslation();
  const {
    fft_window, setFFTWindow, octave_shift, setOctaveShift, ui_scale,
    filter_auto_gain, updateFilter
  } = useStore();

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="h-6 border-b-[width:var(--ui-border)] flex items-center px-4 font-bold text-[0.625rem] uppercase tracking-widest shrink-0 bg-surface justify-between"
           style={{ borderBottomColor: 'var(--color-grid)' }}>
        <span className="opacity-50">{t('views.spectrum_analyzer')}</span>

        <div className="flex items-center gap-4 h-full">
            {/* Auto-Gain Toggle */}
            <div className="flex items-center h-full border-l border-white/10 pl-4">
                <Tooltip content={t('settings.filter_auto_gain_desc')}>
                    <button
                        onClick={() => updateFilter({ auto_gain: !filter_auto_gain })}
                        className={`px-2 py-0.5 rounded-[var(--ui-radius)] text-[0.5rem] font-bold uppercase tracking-tighter transition-all active:scale-95 border ${
                            filter_auto_gain
                                ? 'bg-accent text-background border-accent'
                                : 'bg-white/5 text-text/40 hover:text-text/60 border-white/10'
                        }`}
                        style={{ borderWidth: 'var(--ui-border)' }}
                    >
                        {t('settings.filter_auto_gain')}
                    </button>
                </Tooltip>
            </div>

            {/* FFT Window */}
            <div className="flex items-center gap-2 h-full border-l border-white/10 pl-4">
                <span className="text-[0.5625rem] opacity-60 font-bold">FFT</span>
                <Tooltip content={t('views.fft_window', { val: fft_window.toFixed(2) })} shortcut={`${t('keys.shift')} + ${t('keys.up_down')}`}>
                    <input type="range" min="0.05" max="1.0" step="0.05" value={fft_window}
                        onChange={(e) => setFFTWindow(parseFloat(e.target.value))}
                        className="w-32 accent-current" />
                </Tooltip>
                <span className="text-[0.625rem] font-mono w-8">{fft_window.toFixed(2)}s</span>
            </div>

            {/* Octave Shift */}
            <div className="flex items-center gap-1 h-full border-l-[width:var(--ui-border)] border-white/10 pl-4">
                <span className="text-[0.5625rem] opacity-60 font-bold mr-1">OCT</span>
                <Tooltip content={t('views.octave_down')} shortcut={`${t('keys.shift')} + ← / A`}>
                    <button onClick={() => setOctaveShift(octave_shift - 1)} className="p-0.5 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronDown size={12 * ui_scale}/></button>
                </Tooltip>
                <span className="text-[0.625rem] font-mono w-4 text-center">{octave_shift > 0 ? `+${octave_shift}` : octave_shift}</span>
                <Tooltip content={t('views.octave_up')} shortcut={`${t('keys.shift')} + → / D`}>
                    <button onClick={() => setOctaveShift(octave_shift + 1)} className="p-0.5 hover:bg-white/10 rounded-[var(--ui-radius)]"><ChevronUp size={12 * ui_scale}/></button>
                </Tooltip>
            </div>
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <Spectrum />
      </div>
    </div>
  );
};
