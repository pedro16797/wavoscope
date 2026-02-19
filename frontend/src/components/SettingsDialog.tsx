import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { ChevronDown } from 'lucide-react';

interface SettingsDialogProps {
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { t } = useTranslation();
  const {
    themes, currentTheme, locales, fetchLocales, language,
    click_volume, spectrum_keys, default_output_folder,
    musicxml_author, updateConfig, time_signature, updateTimeSignature
  } = useStore();

  const [activeTab, setActiveTab] = useState<'global' | 'project' | 'keybinds'>('global');

  const [theme, setTheme] = useState(currentTheme);
  const [lang, setLang] = useState(language);
  const [clickVol, setClickVol] = useState(click_volume * 100);
  const [keys, setKeys] = useState(spectrum_keys);
  const [outputFolder, setOutputFolder] = useState(default_output_folder);
  const [author, setAuthor] = useState(musicxml_author);
  const [timeSig, setTimeSig] = useState(time_signature);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDenDropdownOpen, setIsDenDropdownOpen] = useState(false);

  useEffect(() => {
    fetchLocales();
  }, [fetchLocales]);

  const handleSave = async () => {
    updateConfig({
        theme,
        language: lang,
        click_volume: clickVol / 100,
        spectrum_keys: keys,
        default_output_folder: outputFolder,
        musicxml_author: author
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
            <button onClick={() => setActiveTab('global')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'global' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                {t('settings.global')}
            </button>
            <button onClick={() => setActiveTab('project')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'project' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                {t('settings.project')}
            </button>
            <button onClick={() => setActiveTab('keybinds')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'keybinds' ? 'bg-white/5 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                {t('settings.keybinds')}
            </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)' }}>
            {activeTab === 'global' ? (
                <>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.theme')}</label>
                        <div className="relative">
                            <button onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                    className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 flex justify-between items-center text-sm text-text outline-none focus:border-accent transition-colors"
                                    style={{ borderWidth: 'var(--ui-border)' }}>
                                <span>{theme}</span>
                                <ChevronDown size={14} className={`transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
                            </button>
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
                        <input type="range" min="0" max="100" value={clickVol} onChange={(e) => setClickVol(parseInt(e.target.value))}
                               className="w-full accent-accent" />
                    </div>
                    <div className="space-y-2">
                        <label htmlFor="language-select" className="text-[10px] uppercase font-bold opacity-50">{t('settings.language')}</label>
                        <select id="language-select" value={lang} onChange={(e) => setLang(e.target.value)}
                                className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm text-text outline-none focus:border-accent"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {locales.map(l => (
                                <option key={l.code} value={l.code}>{l.name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.keys')}</label>
                        <input type="number" min="12" max="120" value={keys} onChange={(e) => setKeys(parseInt(e.target.value))}
                               className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm font-mono text-text accent-accent"
                               style={{ borderWidth: 'var(--ui-border)' }} />
                    </div>
                </>
            ) : activeTab === 'project' ? (
                <>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] uppercase font-bold opacity-50">{t('settings.measure_calc')}</label>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 space-y-1">
                                    <label htmlFor="time-sig-num" className="text-[9px] opacity-40 uppercase">{t('settings.numerator')}</label>
                                    <input id="time-sig-num" type="number" min="1" max="32" value={timeSig.numerator}
                                           onChange={(e) => setTimeSig({...timeSig, numerator: parseInt(e.target.value)})}
                                           className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent accent-accent"
                                           style={{ borderWidth: 'var(--ui-border)' }} />
                                </div>
                                <div className="text-xl opacity-20 mt-4">/</div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-[9px] opacity-40 uppercase font-bold">{t('settings.denominator')}</label>
                                    <div className="relative">
                                        <button onClick={() => setIsDenDropdownOpen(!isDenDropdownOpen)}
                                                className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 flex justify-between items-center text-sm font-mono text-text outline-none focus:border-accent transition-colors"
                                                style={{ borderWidth: 'var(--ui-border)' }}>
                                            <span>{timeSig.denominator}</span>
                                            <ChevronDown size={14} className={`transition-transform duration-200 ${isDenDropdownOpen ? 'rotate-180' : ''}`} />
                                        </button>
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
                                    <input id="output-folder" type="text" value={outputFolder}
                                           onChange={(e) => setOutputFolder(e.target.value)}
                                           placeholder="e.g. /Users/Name/Documents"
                                           className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                           style={{ borderWidth: 'var(--ui-border)' }} />
                                </div>
                                <div className="space-y-1">
                                    <label htmlFor="musicxml-author" className="text-[9px] opacity-40 uppercase font-bold">{t('settings.author')}</label>
                                    <input id="musicxml-author" type="text" value={author}
                                           onChange={(e) => setAuthor(e.target.value)}
                                           placeholder="Your Name"
                                           className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                           style={{ borderWidth: 'var(--ui-border)' }} />
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="space-y-4 text-xs">
                    <div className="font-bold border-b border-grid pb-1 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.keybinds')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_play_pause')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Space</span>
                        <span className="opacity-60">{t('settings.kb_seek')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">← / →</span>
                        <span className="opacity-60">{t('settings.kb_speed')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">↑ / ↓</span>
                        <span className="opacity-60">{t('settings.kb_rhythm')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">B</span>
                        <span className="opacity-60">{t('settings.kb_harmony')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">H</span>
                        <span className="opacity-60">{t('settings.kb_lyrics')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">L</span>
                        <span className="opacity-60">{t('settings.kb_delete')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Del / Bksp</span>
                        <span className="opacity-60">{t('settings.kb_open')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Ctrl+O</span>
                        <span className="opacity-60">{t('settings.kb_save')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Ctrl+S</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.transcription')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_add_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Space</span>
                        <span className="opacity-60">{t('settings.kb_finish_edit')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Enter</span>
                        <span className="opacity-60">{t('settings.kb_move_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">← / →</span>
                        <span className="opacity-60">{t('settings.kb_resize_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">↑ / ↓</span>
                        <span className="opacity-60">{t('settings.kb_jump_word')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Shift + ← / →</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.interactions')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_rhythm')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Left Click</span>
                        <span className="opacity-60">{t('settings.kb_harmony')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click</span>
                        <span className="opacity-60">{t('settings.kb_move_flag')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Left Drag</span>
                        <span className="opacity-60">{t('settings.kb_audition')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Hold Click</span>
                        <span className="opacity-60">{t('settings.kb_scroll')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Mouse Wheel</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">{t('settings.waveform_spectrum')}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">{t('settings.kb_seek_playhead')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Waveform Click</span>
                        <span className="opacity-60">{t('settings.kb_pan')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Waveform Drag</span>
                        <span className="opacity-60">{t('settings.kb_zoom')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Mouse Wheel</span>
                        <span className="opacity-60">{t('settings.kb_play_note')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Spectrum Click</span>
                        <span className="opacity-60">{t('settings.kb_toggle_cutoff')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click handle</span>
                        <span className="opacity-60">{t('settings.kb_place_cutoff')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click</span>
                        <span className="opacity-60">{t('settings.kb_adjust_cutoff')}</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Handle Drag</span>
                    </div>
                </div>
            )}
        </div>

        <div className="p-4 border-t-[var(--ui-border)] border-grid flex items-center justify-end gap-2 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderTopWidth: 'var(--ui-border)' }}>
            <button onClick={onClose} className="px-4 py-2 rounded-[var(--ui-radius)] hover:bg-white/10 text-xs transition-colors font-bold">{t('common.cancel')}</button>
            <button onClick={handleSave} className="px-4 py-2 rounded-[var(--ui-radius)] bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">{t('common.apply')}</button>
        </div>
      </div>
    </div>
  );
};
