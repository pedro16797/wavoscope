import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { ChevronDown } from 'lucide-react';

interface SettingsDialogProps {
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { themes, currentTheme, click_volume, spectrum_keys, default_output_folder, musicxml_author, updateConfig, time_signature, updateTimeSignature } = useStore();
  const [activeTab, setActiveTab] = useState<'global' | 'project' | 'keybinds'>('global');

  const [theme, setTheme] = useState(currentTheme);
  const [clickVol, setClickVol] = useState(click_volume * 100);
  const [keys, setKeys] = useState(spectrum_keys);
  const [outputFolder, setOutputFolder] = useState(default_output_folder);
  const [author, setAuthor] = useState(musicxml_author);
  const [timeSig, setTimeSig] = useState(time_signature);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDenDropdownOpen, setIsDenDropdownOpen] = useState(false);

  const handleSave = async () => {
    updateConfig({
        theme,
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
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>Settings</div>

        <div className="flex border-b-[var(--ui-border)] border-grid bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>
            <button onClick={() => setActiveTab('global')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'global' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                Global
            </button>
            <button onClick={() => setActiveTab('project')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'project' ? 'bg-accent/10 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                Project
            </button>
            <button onClick={() => setActiveTab('keybinds')}
                    className={`flex-1 p-3 text-[10px] font-bold uppercase tracking-wider transition-colors ${activeTab === 'keybinds' ? 'bg-white/5 border-b-2 border-accent text-accent' : 'opacity-50 hover:opacity-100'}`}>
                Keybinds
            </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)' }}>
            {activeTab === 'global' ? (
                <>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">UI Theme</label>
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
                            <span>Click Volume</span>
                            <span className="font-mono">{Math.round(clickVol)}%</span>
                        </label>
                        <input type="range" min="0" max="100" value={clickVol} onChange={(e) => setClickVol(parseInt(e.target.value))}
                               className="w-full accent-accent" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">Visible Piano Keys</label>
                        <input type="number" min="12" max="120" value={keys} onChange={(e) => setKeys(parseInt(e.target.value))}
                               className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm font-mono text-text accent-accent"
                               style={{ borderWidth: 'var(--ui-border)' }} />
                    </div>
                </>
            ) : activeTab === 'project' ? (
                <>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-[10px] uppercase font-bold opacity-50">Measure Calculation</label>
                            <div className="flex items-center gap-4">
                                <div className="flex-1 space-y-1">
                                    <label htmlFor="time-sig-num" className="text-[9px] opacity-40 uppercase">Numerator</label>
                                    <input id="time-sig-num" type="number" min="1" max="32" value={timeSig.numerator}
                                           onChange={(e) => setTimeSig({...timeSig, numerator: parseInt(e.target.value)})}
                                           className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent accent-accent"
                                           style={{ borderWidth: 'var(--ui-border)' }} />
                                </div>
                                <div className="text-xl opacity-20 mt-4">/</div>
                                <div className="flex-1 space-y-1">
                                    <label className="text-[9px] opacity-40 uppercase font-bold">Denominator</label>
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
                                Used for MusicXML export to determine measure structure and tempo calculation.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] uppercase font-bold opacity-50">Export Defaults</label>
                            <div className="space-y-4 bg-black/20 p-4 rounded-[var(--ui-radius)] border border-grid">
                                <div className="space-y-1">
                                    <label htmlFor="output-folder" className="text-[9px] opacity-40 uppercase font-bold">Default Output Directory</label>
                                    <input id="output-folder" type="text" value={outputFolder}
                                           onChange={(e) => setOutputFolder(e.target.value)}
                                           placeholder="e.g. /Users/Name/Documents"
                                           className="w-full bg-background border border-grid rounded-[var(--ui-radius)] p-2 text-sm font-mono text-text outline-none focus:border-accent"
                                           style={{ borderWidth: 'var(--ui-border)' }} />
                                </div>
                                <div className="space-y-1">
                                    <label htmlFor="musicxml-author" className="text-[9px] opacity-40 uppercase font-bold">MusicXML Author (Composer)</label>
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
                    <div className="font-bold border-b border-grid pb-1 mb-2 opacity-50 uppercase tracking-tighter">Keyboard Bindings</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">Play / Pause</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Space</span>
                        <span className="opacity-60">Seek Forward/Back</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">← / →</span>
                        <span className="opacity-60">Adjust Speed</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">↑ / ↓</span>
                        <span className="opacity-60">Add Rhythm Flag</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">B</span>
                        <span className="opacity-60">Add Harmony Flag</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">H</span>
                        <span className="opacity-60">Toggle Lyrics</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">L</span>
                        <span className="opacity-60">Delete Selected</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Del / Bksp</span>
                        <span className="opacity-60">Open File</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Ctrl+O</span>
                        <span className="opacity-60">Save Project</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Ctrl+S</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">Lyrics Transcription</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">Add Word (Editing)</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Space</span>
                        <span className="opacity-60">Finish Editing</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Enter</span>
                        <span className="opacity-60">Move Word</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">← / →</span>
                        <span className="opacity-60">Resize Word</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">↑ / ↓</span>
                        <span className="opacity-60">Jump to Word</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Shift + ← / →</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">Timeline Interactions</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">Add Rhythm Flag</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Left Click</span>
                        <span className="opacity-60">Add Harmony Flag</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click</span>
                        <span className="opacity-60">Move Flag</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Left Drag</span>
                        <span className="opacity-60">Audition Harmony</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Hold Click</span>
                    </div>

                    <div className="font-bold border-b border-grid pb-1 mt-6 mb-2 opacity-50 uppercase tracking-tighter">Waveform & Spectrum</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                        <span className="opacity-60">Seek Playhead</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Waveform Click</span>
                        <span className="opacity-60">Pan View</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Waveform Drag</span>
                        <span className="opacity-60">Zoom View</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Mouse Wheel</span>
                        <span className="opacity-60">Play Note</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Spectrum Click</span>
                        <span className="opacity-60">Toggle Cutoff</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click handle</span>
                        <span className="opacity-60">Place Cutoff</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Right Click</span>
                        <span className="opacity-60">Adjust Cutoff</span> <span className="font-mono bg-white/5 px-1 rounded text-accent">Handle Drag</span>
                    </div>
                </div>
            )}
        </div>

        <div className="p-4 border-t-[var(--ui-border)] border-grid flex items-center justify-end gap-2 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderTopWidth: 'var(--ui-border)' }}>
            <button onClick={onClose} className="px-4 py-2 rounded-[var(--ui-radius)] hover:bg-white/10 text-xs transition-colors font-bold">Cancel</button>
            <button onClick={handleSave} className="px-4 py-2 rounded-[var(--ui-radius)] bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">Apply Settings</button>
        </div>
      </div>
    </div>
  );
};
