import React, { useState } from 'react';
import { useStore } from '../store/useStore';

interface SettingsDialogProps {
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { themes, currentTheme, click_gain, spectrum_keys, updateConfig } = useStore();
  const [activeTab, setActiveTab] = useState<'global' | 'keybinds'>('global');

  const [theme, setTheme] = useState(currentTheme);
  const [clickVol, setClickVol] = useState(click_gain * 100);
  const [keys, setKeys] = useState(spectrum_keys);

  const handleSave = () => {
    updateConfig({
        theme,
        click_volume: clickVol / 100,
        spectrum_keys: keys
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-surface border border-grid rounded-lg shadow-xl w-full max-w-md overflow-hidden text-text flex flex-col max-h-[80vh]">
        <div className="p-4 border-b border-grid font-bold">Settings</div>

        <div className="flex border-b border-grid">
            <button onClick={() => setActiveTab('global')}
                    className={`flex-1 p-3 text-xs font-bold uppercase tracking-wider transition-colors ${activeTab === 'global' ? 'bg-white/5 border-b-2 border-accent' : 'opacity-50 hover:opacity-100'}`}>
                Global
            </button>
            <button onClick={() => setActiveTab('keybinds')}
                    className={`flex-1 p-3 text-xs font-bold uppercase tracking-wider transition-colors ${activeTab === 'keybinds' ? 'bg-white/5 border-b-2 border-accent' : 'opacity-50 hover:opacity-100'}`}>
                Keybinds
            </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {activeTab === 'global' ? (
                <>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">UI Theme</label>
                        <select value={theme} onChange={(e) => setTheme(e.target.value)}
                                className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent">
                            {Object.keys(themes).map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50 flex justify-between">
                            <span>Click Volume</span>
                            <span>{Math.round(clickVol)}%</span>
                        </label>
                        <input type="range" min="0" max="100" value={clickVol} onChange={(e) => setClickVol(parseInt(e.target.value))}
                               className="w-full accent-accent" />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] uppercase font-bold opacity-50">Visible Piano Keys</label>
                        <input type="number" min="12" max="120" value={keys} onChange={(e) => setKeys(parseInt(e.target.value))}
                               className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent" />
                    </div>
                </>
            ) : (
                <div className="space-y-4 opacity-50 italic text-center py-10 text-xs">
                    Keybind editing is coming soon in the React port.
                    Use the legacy Qt GUI or edit config files for now.
                </div>
            )}
        </div>

        <div className="p-4 bg-background/50 border-t border-grid flex items-center justify-end gap-2">
            <button onClick={onClose} className="px-4 py-2 rounded hover:bg-white/5 text-xs transition-colors">Cancel</button>
            <button onClick={handleSave} className="px-4 py-2 rounded bg-accent text-background text-xs font-bold transition-colors">Apply</button>
        </div>
      </div>
    </div>
  );
};
