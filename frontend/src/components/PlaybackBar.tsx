import React from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { Play, Pause, Square, Volume2, Settings, Timer, FolderOpen, Save, Repeat, Repeat1, FileDown } from 'lucide-react';
import { Tooltip } from './Tooltip';

export const PlaybackBar: React.FC = () => {
  const { t } = useTranslation();
  const {
    loaded, position, duration, playing, speed, volume, filename, metadata,
    controlPlayback, currentTheme, themes,
    metronome_enabled, updateMetronome, setShowSettings, browseFile,
    saveProject, exportMusicXML, dirty, loop_mode, cycleLoopMode
  } = useStore();

  const theme = themes[currentTheme] || {};

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (position / duration) * 100 : 0;


  const getLoopIcon = () => {
    if (loop_mode === 'bar' || loop_mode === 'lyric') return <Repeat1 size={20} />;
    return <Repeat size={20} />;
  };

  const getLoopTitle = () => {
    switch (loop_mode) {
        case 'whole': return t('playback.loop_whole');
        case 'section': return t('playback.loop_section');
        case 'bar': return t('playback.loop_bar');
        case 'lyric': return t('playback.loop_lyric');
        default: return t('playback.loop_off');
    }
  };

  const getHeaderText = () => {
    if (!loaded) return t('common.ready');
    const parts = [];
    if (metadata.title) parts.push(metadata.title);
    if (metadata.artist) parts.push(metadata.artist);
    if (metadata.album) parts.push(`(${metadata.album})`);

    if (parts.length > 0) return parts.join(' - ');
    return filename;
  };

  return (
    <div className="p-2 flex items-center gap-4 border-b-[width:var(--ui-border)] select-none h-16 shrink-0 bg-surface" style={{ color: theme.text }}>
      <div className="flex items-center gap-1">
        <Tooltip content={t('playback.open')} shortcut={`${t('keys.ctrl')}+O`}>
            <button onClick={browseFile} aria-label={t('playback.open')} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors">
                <FolderOpen size={20} />
            </button>
        </Tooltip>
        <Tooltip content={dirty ? t('playback.save_dirty') : t('playback.save_clean')} shortcut={`${t('keys.ctrl')}+S`}>
            <button onClick={saveProject} disabled={!loaded} aria-label={t('playback.save_clean')}
                    className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors ${!loaded ? 'opacity-20' : 'opacity-90'}`}>
                <Save size={20} className={dirty ? 'text-accent' : 'text-text'} />
            </button>
        </Tooltip>
        <Tooltip content={t('playback.export_xml')} shortcut={`${t('keys.ctrl')}+E`}>
            <button onClick={exportMusicXML} disabled={!loaded} aria-label={t('playback.export_xml')}
                    className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors mr-2 ${!loaded ? 'opacity-20' : 'opacity-90'}`}>
                <FileDown size={20} />
            </button>
        </Tooltip>
        {loaded && (
            <>
                <Tooltip content={playing ? t('playback.pause') : t('playback.play')} shortcut={t('keys.space')}>
                    <button onClick={() => controlPlayback(playing ? 'pause' : 'play')}
                            aria-label={playing ? t('playback.pause') : t('playback.play')}
                            className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors">
                    {playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
                    </button>
                </Tooltip>
                <Tooltip content={t('playback.stop')} shortcut={`${t('keys.shift')}+${t('keys.space')}`}>
                    <button onClick={() => controlPlayback('stop')}
                            aria-label={t('playback.stop')}
                            className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors mr-1">
                    <Square size={20} fill="currentColor" />
                    </button>
                </Tooltip>
                <Tooltip content={getLoopTitle()} shortcut={t('keys.tab')}>
                    <button onClick={() => cycleLoopMode()} aria-label={getLoopTitle()}
                            className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors relative ${loop_mode !== 'none' ? 'text-accent' : 'opacity-40'}`}>
                        {getLoopIcon()}
                        {loop_mode === 'section' && <span className="absolute top-1 right-1 text-[8px] font-bold bg-accent text-surface rounded-full w-3 h-3 flex items-center justify-center border border-surface shadow-sm">S</span>}
                        {loop_mode === 'lyric' && <span className="absolute top-1 right-1 text-[8px] font-bold bg-accent text-surface rounded-full w-3 h-3 flex items-center justify-center border border-surface shadow-sm">L</span>}
                    </button>
                </Tooltip>
                {/* Metronome */}
                <Tooltip content={t('playback.metronome')} shortcut="M">
                    <button onClick={() => updateMetronome(!metronome_enabled)} aria-label={t('playback.metronome')}
                            className={`p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors ${metronome_enabled ? 'text-accent bg-accent/10' : 'opacity-40'}`}>
                        <Timer size={18} />
                    </button>
                </Tooltip>
            </>
        )}
      </div>

      <div className="flex-1 flex flex-col justify-center gap-1 min-w-0 px-4">
        <Tooltip content={loaded ? filename : ''}>
            <div className="text-xs font-bold truncate opacity-80">
                {getHeaderText()}
            </div>
        </Tooltip>
        <div className="flex items-center gap-3 text-[11px] font-mono">
            <span className="w-12 text-right">{formatTime(position)}</span>
            <Tooltip content={t('settings.kb_seek_playhead')} shortcut={t('keys.left_right')}>
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
            </Tooltip>
            <span className="w-10">{formatTime(duration)}</span>
        </div>
      </div>

      <div className="flex items-center gap-4 pr-2">
        {/* Speed & Volume */}
        <div className="flex items-center gap-2 border-l-[width:var(--ui-border)] border-white/10 pl-4">
            <Tooltip content={t('settings.kb_speed')} shortcut={t('keys.up_down')}>
                <span className="text-[9px] opacity-60 font-bold">{t('playback.speed')}</span>
            </Tooltip>
            <Tooltip content={t('settings.kb_speed')} shortcut={t('keys.up_down')}>
                <input type="range" min="0.1" max="2" step="0.1" value={speed}
                    onChange={(e) => controlPlayback('set_speed', parseFloat(e.target.value))}
                    className="w-16 accent-current" />
            </Tooltip>
            <span className="text-[10px] font-mono w-8">{speed.toFixed(1)}x</span>
        </div>
        <div className="flex items-center gap-2">
            <Tooltip content={t('playback.volume_desc')}>
                <Volume2 size={16} className="opacity-60" />
            </Tooltip>
            <Tooltip content={t('playback.volume_desc')}>
                <input type="range" min="0" max="1" step="0.05" value={volume}
                    onChange={(e) => controlPlayback('set_volume', parseFloat(e.target.value))}
                    className="w-16 accent-current" />
            </Tooltip>
        </div>

        <Tooltip content={t('playback.settings')} shortcut="Esc">
            <button onClick={() => setShowSettings(true)} aria-label={t('playback.settings')} className="p-2 hover:bg-white/10 rounded-[var(--ui-radius)] transition-colors">
                <Settings size={18} />
            </button>
        </Tooltip>
      </div>
    </div>
  );
};
