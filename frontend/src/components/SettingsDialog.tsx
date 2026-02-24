import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { ChevronDown, FolderOpen } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface SettingsDialogProps {
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { t } = useTranslation();
  const {
    themes, currentTheme, locales, fetchLocales, language,
    audioDevices, fetchAudioDevices, audio_device,
    click_volume, spectrum_keys, default_output_folder,
    musicxml_author, updateConfig, time_signature, updateTimeSignature,
    browseFolder, autosave_enabled, autosave_forced, autosave_interval,
    autosave_max_snapshots, autosave_path
  } = useStore();

  const [activeTab, setActiveTab] = useState<'global' | 'project' | 'autosave' | 'keybinds'>('global');

  const [theme, setTheme] = useState(currentTheme);
  const [lang, setLang] = useState(language);
  const [audioDev, setAudioDev] = useState(audio_device);
  const [clickVol, setClickVol] = useState(click_volume * 100);
  const [keys, setKeys] = useState(spectrum_keys);
  const [outputFolder, setOutputFolder] = useState(default_output_folder);
  const [author, setAuthor] = useState(musicxml_author);
  const [timeSig, setTimeSig] = useState(time_signature);
  const [asEnabled, setAsEnabled] = useState(autosave_enabled);
  const [asForced, setAsForced] = useState(autosave_forced);
  const [asInterval, setAsInterval] = useState(autosave_interval);
  const [asMaxSnapshots, setAsMaxSnapshots] = useState(autosave_max_snapshots);
  const [asPath, setAsPath] = useState(autosave_path);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDenDropdownOpen, setIsDenDropdownOpen] = useState(false);

  useEffect(() => {
    fetchLocales();
    fetchAudioDevices();
  }, [fetchLocales, fetchAudioDevices]);

  const handleSave = async () => {
    updateConfig({
        theme,
        language: lang,
        audio_device: audioDev,
        click_volume: clickVol / 100,
        spectrum_keys: keys,
        default_output_folder: outputFolder,
        musicxml_author: author,
        autosave_enabled: asEnabled,
        autosave_forced: asForced,
        autosave_interval: asInterval,
        autosave_max_snapshots: asMaxSnapshots,
        autosave_path: asPath
    });
    await updateTimeSignature(timeSig.numerator, timeSig.denominator);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] shadow-2xl w-full max-w-md overflow-hidden text-text flex flex-col max-h-[80vh] isolation-auto"
           style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}
           onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b-[var(--ui-border)] border-grid font-bold text-sm uppercase tracking-widest opacity-80 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>{t('settings.title')}</div>

        <div className="flex border-b-[var(--ui-border)] border-grid bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>
            <Tooltip content={t('settings.global_desc')} className="flex-1">
                <button onClick={() => setActiveTab('global')}
                        className={`w-full p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'global' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                    {t('settings.global')}
                </button>
            </Tooltip>
            <Tooltip content={t('settings.project_desc')} className="flex-1">
                <button onClick={() => setActiveTab('project')}
                        className={`w-full p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'project' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                    {t('settings.project')}
                </button>
            </Tooltip>
            <Tooltip content={t('settings.autosave_desc')} className="flex-1">
                <button onClick={() => setActiveTab('autosave')}
                        className={`w-full p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'autosave' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                    {t('settings.autosave')}
                </button>
            </Tooltip>
            <Tooltip content={t('settings.keybinds_desc')} className="flex-1">
                <button onClick={() => setActiveTab('keybinds')}
                        className={`w-full p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'keybinds' ? 'bg-white/5 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                    {t('settings.keybinds')}
                </button>
            </Tooltip>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)' }}>
            {activeTab === 'global' ? (
                <>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.theme')}</label>
                        <div className="relative">
                            <Tooltip content={t('settings.theme_desc')} className="w-full">
                                <button onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                        className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 flex justify-between items-center text-sm text-text outline-none focus:border-accent transition-colors"
                                        style={{ borderWidth: 'var(--ui-border)' }}>
                                    <span>{theme}</span>
                                    <ChevronDown size={14} className={`transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
                                </button>
                            </Tooltip>
                            {isDropdownOpen && (
                                <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-grid rounded-[var(--ui-radius)] shadow-2xl z-50 overflow-hidden"
                                     style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}>
                                    <div className="max-h-48 overflow-y-auto">
                                        {Object.keys(themes).map(t => (
                                            <button key={t}
                                                    onClick={() => { setTheme(t); setIsDropdownOpen(false); }}
                                                    className={`w-full text-left px-3 py-2 text-sm transition-colors ${theme === t ? 'bg-accent text-background font-bold' : 'hover:bg-accent/20 text-text'}`}>
                                                {t}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50 flex justify-between">
                            <span>{t('settings.volume')}</span>
                            <span className="font-mono">{Math.round(clickVol)}%</span>
                        </label>
                        <Tooltip content={t('settings.volume_desc')} className="w-full">
                            <input type="range" min="0" max="100" value={clickVol} onChange={(e) => setClickVol(parseInt(e.target.value))}
                                className="w-full accent-accent" />
                        </Tooltip>
                    </div>
                    <div className="space-y-2">
                        <label htmlFor="language-select" className="text-[10px] uppercase font-bold opacity-50">{t('settings.language')}</label>
                        <Tooltip content={t('settings.language_desc')} className="w-full">
                            <select id="language-select" value={lang} onChange={(e) => setLang(e.target.value)}
                                    className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm text-text outline-none focus:border-accent"
                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                {locales.map(l => (
                                    <option key={l.code} value={l.code}>{l.name}</option>
                                ))}
                            </select>
                        </Tooltip>
                    </div>
                    <div className="space-y-2">
                        <label htmlFor="audio-device-select" className="text-[10px] uppercase font-bold opacity-50">{t('settings.audio_device')}</label>
                        <Tooltip content={t('settings.audio_device_desc')} className="w-full">
                            <select id="audio-device-select" value={audioDev} onChange={(e) => setAudioDev(e.target.value)}
                                    className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm text-text outline-none focus:border-accent"
                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                <option value="">{t('settings.default_device')}</option>
                                {audioDevices.map(d => (
                                    <option key={`${d.index}-${d.name}`} value={d.name}>{d.name}</option>
                                ))}
                            </select>
                        </Tooltip>
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.keys')}</label>
                        <Tooltip content={t('settings.keys_desc')} className="w-full">
                            <input type="number" min="12" max="120" value={keys} onChange={(e) => setKeys(parseInt(e.target.value))}
                                className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm font-mono text-text accent-accent"
                                style={{ borderWidth: 'var(--ui-border)' }} />
                        </Tooltip>
                    </div>

                </>
            ) : activeTab === 'autosave' ? (
                <div className="space-y-6">
                    <div className="space-y-4">
                        <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.autosave')}</label>

                        <div className="flex items-center justify-between">
                            <span className="text-sm opacity-80">{t('settings.autosave_enabled')}</span>
                            <Tooltip content={t('settings.autosave_enabled_desc')}>
                                <button onClick={() => setAsEnabled(!asEnabled)}
                                        className={`w-10 h-5 rounded-full transition-colors relative ${asEnabled ? 'bg-accent' : 'bg-grid'}`}>
                                    <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${asEnabled ? 'left-6' : 'left-1'}`} />
                                </button>
                            </Tooltip>
                        </div>

                        {asEnabled && (
                            <div className="space-y-4 pl-2 border-l-2 border-accent/20 animate-in fade-in slide-in-from-left-1">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm opacity-80">{t('settings.autosave_forced')}</span>
                                    <Tooltip content={t('settings.autosave_forced_desc')}>
                                        <button onClick={() => setAsForced(!asForced)}
                                                className={`w-10 h-5 rounded-full transition-colors relative ${asForced ? 'bg-accent' : 'bg-grid'}`}>
                                            <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${asForced ? 'left-6' : 'left-1'}`} />
                                        </button>
                                    </Tooltip>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.autosave_interval')}</label>
                                    <Tooltip content={t('settings.autosave_interval_desc')} className="w-full">
                                        <input type="number" min="1" max="60" value={asInterval} onChange={(e) => setAsInterval(parseInt(e.target.value))}
                                            className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                            style={{ borderWidth: 'var(--ui-border)' }} />
                                    </Tooltip>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.autosave_snapshots')}</label>
                                    <Tooltip content={t('settings.autosave_snapshots_desc')} className="w-full">
                                        <input type="number" min="1" max="50" value={asMaxSnapshots} onChange={(e) => setAsMaxSnapshots(parseInt(e.target.value))}
                                            className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                            style={{ borderWidth: 'var(--ui-border)' }} />
                                    </Tooltip>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.autosave_path')}</label>
                                    <div className="flex gap-2">
                                        <Tooltip content={t('settings.autosave_path_desc')} className="flex-1">
                                            <input type="text" value={asPath}
                                                onChange={(e) => setAsPath(e.target.value)}
                                                placeholder={t('settings.autosave_path_hint')}
                                                className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-xs font-mono text-text outline-none focus:border-accent"
                                                style={{ borderWidth: 'var(--ui-border)' }} />
                                        </Tooltip>
                                        <Tooltip content={t('settings.browse')}>
                                            <button onClick={async () => {
                                                        let initial = asPath;
                                                        if (!initial) {
                                                            try {
                                                                const resp = await fetch(`${window.location.origin}/config/temp-dir`);
                                                                const data = await resp.json();
                                                                initial = data.temp_dir;
                                                            } catch (e) {
                                                                console.error("Failed to fetch temp dir", e);
                                                            }
                                                        }
                                                        const res = await browseFolder(initial);
                                                        if (res) setAsPath(res);
                                                    }}
                                                    className="bg-background border border-grid rounded-[var(--ui-radius)] px-3 py-2 hover:bg-white/5 transition-colors text-accent"
                                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                                <FolderOpen size={16} />
                                            </button>
                                        </Tooltip>
                                    </div>
                                    <p className="text-[9px] opacity-40">{t('settings.autosave_path_hint')}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ) : activeTab === 'project' ? (
                <>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.measure_calc')}</label>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 space-y-1">
                                    <label htmlFor="time-sig-num" className="text-[9px] opacity-40 uppercase">{t('settings.numerator')}</label>
                                    <Tooltip content={t('settings.numerator_desc')} className="w-full">
                                        <input id="time-sig-num" type="number" min="1" max="32" value={timeSig.numerator}
                                            onChange={(e) => setTimeSig({...timeSig, numerator: parseInt(e.target.value)})}
                                            className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent accent-accent"
                                            style={{ borderWidth: 'var(--ui-border)' }} />
                                    </Tooltip>
                                </div>
                                <div className="text-xl opacity-20 mt-4">/</div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-[9px] opacity-40 uppercase font-bold">{t('settings.denominator')}</label>
                                    <div className="relative">
                                        <Tooltip content={t('settings.denominator_desc')} className="w-full">
                                            <button onClick={() => setIsDenDropdownOpen(!isDenDropdownOpen)}
                                                    className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 flex justify-between items-center text-sm font-mono text-text outline-none focus:border-accent transition-colors"
                                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                                <span>{timeSig.denominator}</span>
                                                <ChevronDown size={14} className={`transition-transform duration-200 ${isDenDropdownOpen ? 'rotate-180' : ''}`} />
                                            </button>
                                        </Tooltip>
                                        {isDenDropdownOpen && (
                                            <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-grid rounded-[var(--ui-radius)] shadow-2xl z-50 overflow-hidden"
                                                 style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}>
                                                {[2, 4, 8, 16].map(d => (
                                                    <button key={d}
                                                            onClick={() => { setTimeSig({...timeSig, denominator: d}); setIsDenDropdownOpen(false); }}
                                                            className={`w-full text-left px-3 py-2 text-sm font-mono transition-colors ${timeSig.denominator === d ? 'bg-accent text-background font-bold' : 'hover:bg-accent/20 text-text'}`}>
                                                        {d}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                            <p className="text-[10px] opacity-40 mt-2">
                                {t('settings.measure_hint')}
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.export_defaults')}</label>
                            <div className="space-y-4 bg-black/20 p-4 rounded-[var(--ui-radius)] border border-grid">
                                <div className="space-y-1">
                                    <label htmlFor="output-folder" className="text-[9px] opacity-40 uppercase font-bold">{t('settings.output_dir')}</label>
                                    <div className="flex gap-2">
                                        <Tooltip content={t('settings.output_dir_desc')} className="flex-1">
                                            <input id="output-folder" type="text" value={outputFolder}
                                                onChange={(e) => setOutputFolder(e.target.value)}
                                                placeholder="e.g. /Users/Name/Documents"
                                                className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                                style={{ borderWidth: 'var(--ui-border)' }} />
                                        </Tooltip>
                                        <Tooltip content={t('settings.browse')}>
                                            <button onClick={async () => {
                                                        const res = await browseFolder();
                                                        if (res) setOutputFolder(res);
                                                    }}
                                                    className="bg-background border border-grid rounded-[var(--ui-radius)] px-3 py-2 hover:bg-white/5 transition-colors text-accent"
                                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                                <FolderOpen size={16} />
                                            </button>
                                        </Tooltip>
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <label htmlFor="musicxml-author" className="text-[9px] opacity-40 uppercase font-bold">{t('settings.author')}</label>
                                    <Tooltip content={t('settings.author_desc')} className="w-full">
                                        <input id="musicxml-author" type="text" value={author}
                                            onChange={(e) => setAuthor(e.target.value)}
                                            placeholder="Your Name"
                                            className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                            style={{ borderWidth: 'var(--ui-border)' }} />
                                    </Tooltip>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="space-y-4 text-xs">
                    <div className="font-bold border-b border-grid pb-1 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.keybinds')}</div>
                    <p className="text-[10px] opacity-40 mb-4 italic leading-tight">
                        {t('settings.kb_no_ui_desc')}
                    </p>
                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.transcription')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_lyrics')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">V / {t('keys.left_click')}</span>
                        <span className="opacity-60">{t('settings.kb_add_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.space')}</span>
                        <span className="opacity-60">{t('settings.kb_add_syllable')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">-</span>
                        <span className="opacity-60">{t('settings.kb_finish_edit')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.enter')}</span>
                        <span className="opacity-60">{t('settings.kb_move_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.left_right')} / A / D</span>
                        <span className="opacity-60">{t('settings.kb_resize_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.up_down')} / W / S</span>
                        <span className="opacity-60">{t('settings.kb_jump_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.shift_arrows')} / Shift + A / D</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.interactions')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_rhythm')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">B / {t('keys.left_click')}</span>
                        <span className="opacity-60">{t('settings.kb_rhythm_auto')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.shift')} + {t('keys.left_click')}</span>
                        <span className="opacity-60">{t('settings.kb_harmony')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">C / {t('keys.right_click')}</span>
                        <span className="opacity-60">{t('settings.kb_move_flag')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.left_drag')}</span>
                        <span className="opacity-60">{t('settings.kb_scroll')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.mouse_wheel')}</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.waveform')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_seek_playhead')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.waveform_click')}</span>
                        <span className="opacity-60">{t('settings.kb_pan')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.waveform_drag')}</span>
                        <span className="opacity-60">{t('settings.kb_zoom')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.mouse_wheel')}</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.spectrum')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_play_note')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.spectrum_click')}</span>
                        <span className="opacity-60">{t('settings.kb_place_cutoff')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.right_click')}</span>
                        <span className="opacity-60">{t('settings.kb_adjust_cutoff')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">{t('keys.handle_drag')}</span>
                    </div>
                </div>
            )}
        </div>

        <div className="p-4 border-t-[var(--ui-border)] border-grid flex items-center justify-end gap-2 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderTopWidth: 'var(--ui-border)' }}>
            <Tooltip content={t('common.cancel')} shortcut="Esc">
                <button onClick={onClose} className="px-4 py-2 rounded-[var(--ui-radius)] hover:bg-white/10 text-xs transition-colors font-bold">{t('common.cancel')}</button>
            </Tooltip>
            <Tooltip content={t('common.apply')} shortcut={t('keys.enter')}>
                <button onClick={handleSave} className="px-4 py-2 rounded-[var(--ui-radius)] bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">{t('common.apply')}</button>
            </Tooltip>
        </div>
      </div>
    </div>
  );
};
