import React from 'react';
import { useTheme } from './ThemeContext';
import { X } from 'lucide-react';

interface SettingsDialogProps {
  onClose: () => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({ onClose }) => {
  const { themes, currentThemeName, setTheme } = useTheme();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface p-6 rounded-lg w-96 flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">Settings</h2>
          <button onClick={onClose}><X /></button>
        </div>

        <div>
          <label className="block text-sm text-text-secondary mb-1">Theme</label>
          <select
            value={currentThemeName}
            onChange={(e) => setTheme(e.target.value)}
            className="w-full bg-background p-2 rounded border border-grid"
          >
            {themes.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="bg-accent px-4 py-2 rounded text-white font-bold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
