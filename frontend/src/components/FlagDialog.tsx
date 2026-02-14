import React, { useState } from 'react';
import { useStore, type Flag } from '../store/useStore';
import axios from 'axios';

interface FlagDialogProps {
  idx: number;
  flag: Flag;
  onClose: () => void;
}

export const FlagDialog: React.FC<FlagDialogProps> = ({ idx, flag, onClose }) => {
  const { fetchStatus, duration } = useStore();
  const [name, setName] = useState(flag.name || '');
  const [t, setT] = useState(flag.t);
  const [subdivision, setSubdivision] = useState(flag.subdivision || 0);
  const [sectionStart, setSectionStart] = useState(flag.is_section_start || false);
  const [shaded, setShaded] = useState(flag.shaded_subdivisions || false);

  const handleSave = async () => {
    try {
        await axios.post('http://127.0.0.1:8000/project/flags', {
            t,
            name,
            subdivision,
            is_section_start: sectionStart,
            shaded_subdivisions: shaded
        });
        if (Math.abs(t - flag.t) > 0.001) {
            await axios.delete(`http://127.0.0.1:8000/project/flags/${idx}`);
        }
        fetchStatus();
        onClose();
    } catch (e) {
        console.error(e);
    }
  };

  const handleDelete = async () => {
    try {
        await axios.delete(`http://127.0.0.1:8000/project/flags/${idx}`);
        fetchStatus();
        onClose();
    } catch (e) {
        console.error(e);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-surface border border-grid rounded-lg shadow-xl w-full max-w-sm overflow-hidden text-text">
        <div className="p-4 border-b border-grid font-bold">Edit Flag</div>
        <div className="p-4 space-y-4">
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent" />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Time (s)</label>
                <input type="number" step="0.001" min="0" max={duration} value={t} onChange={(e) => setT(parseFloat(e.target.value))}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent" />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Subdivision</label>
                <input type="number" min="0" max="32" value={subdivision} onChange={(e) => setSubdivision(parseInt(e.target.value))}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent" />
            </div>
            <div className="flex items-center gap-4 py-2">
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={sectionStart} onChange={(e) => setSectionStart(e.target.checked)} className="accent-accent" />
                    <span className="text-xs">Section Start</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={shaded} onChange={(e) => setShaded(e.target.checked)} className="accent-accent" />
                    <span className="text-xs">Shade 8th notes</span>
                </label>
            </div>
        </div>
        <div className="p-4 bg-background/50 border-t border-grid flex items-center justify-between gap-2">
            <button onClick={handleDelete} className="px-4 py-2 rounded bg-red-600/20 hover:bg-red-600/40 text-red-500 text-xs font-bold transition-colors">Delete</button>
            <div className="flex items-center gap-2">
                <button onClick={onClose} className="px-4 py-2 rounded hover:bg-white/5 text-xs transition-colors">Cancel</button>
                <button onClick={handleSave} className="px-4 py-2 rounded bg-accent text-background text-xs font-bold transition-colors">Save</button>
            </div>
        </div>
      </div>
    </div>
  );
};
