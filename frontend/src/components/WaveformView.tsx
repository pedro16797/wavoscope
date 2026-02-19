import React from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { Timeline } from './Timeline';
import { Waveform } from './Waveform';
import { LyricsTimeline } from './LyricsTimeline';
import { Type } from 'lucide-react';
import { Tooltip } from './Tooltip';

export const WaveformView: React.FC = () => {
  const { t } = useTranslation();
  const { showLyrics, setShowLyrics } = useStore();

  return (
    <div className="flex flex-col h-full w-full min-h-0">
      <div className="h-6 border-b-[width:var(--ui-border)] flex items-center justify-between px-4 font-bold text-[10px] opacity-50 uppercase tracking-widest shrink-0 bg-surface"
           style={{ borderBottomColor: 'var(--color-grid)' }}>
        <span>{t('views.timeline_waveform')}</span>
        <Tooltip content={t('views.lyrics_toggle')}>
          <button
            onClick={() => setShowLyrics(!showLyrics)}
            className={`flex items-center gap-1 px-1 rounded transition-colors ${showLyrics ? 'bg-accent text-white opacity-100' : 'hover:bg-white/10'}`}
          >
            <Type size={12} />
            <span>{t('views.lyrics_label')}</span>
          </button>
        </Tooltip>
      </div>
      <Timeline />
      {showLyrics && <LyricsTimeline />}
      <div className="flex-1 min-h-0">
        <Waveform />
      </div>
    </div>
  );
};
