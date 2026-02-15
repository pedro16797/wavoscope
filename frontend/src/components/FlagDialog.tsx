import React, { useState } from 'react';
import { useStore, type Flag } from '../store/useStore';
import axios from 'axios';

interface FlagDialogProps {
  idx: number;
  flag: Flag;
  onClose: () => void;
}

export const FlagDialog: React.FC<FlagDialogProps> = ({ idx, flag, onClose }) => {
  const { fetchStatus, duration, flags } = useStore();

  const [name, setName] = useState(flag?.name || '');
  const [t, setT] = useState(flag?.t || 0);
  const [subdivision, setSubdivision] = useState(flag?.subdivision || 0);
  const [sectionStart, setSectionStart] = useState(flag?.is_section_start || false);
  const [shaded, setShaded] = useState(flag?.shaded_subdivisions || false);

  if (!flag) {
    console.error("FlagDialog opened but flag is missing at index", idx);
    onClose();
    return null;
  }

  const handleSave = async () => {
    try {
        await axios.post('/project/flags', {
            t,
            name,
            subdivision,
            is_section_start: sectionStart,
            shaded_subdivisions: shaded
        });
        if (Math.abs(t - flag.t) > 0.001) {
            await axios.delete(`/project/flags/${idx}`);
        }
        fetchStatus();
        onClose();
    } catch (e) {
        console.error(e);
    }
  };

  const handleDelete = async () => {
    try {
        await axios.delete(`/project/flags/${idx}`);
        fetchStatus();
        onClose();
    } catch (e) {
        console.error(e);
    }
  };

  const handleInsertN = async () => {
    const countStr = prompt("How many flags to insert between this and the next one?", "3");
    if (!countStr) return;
    const count = parseInt(countStr);
    if (isNaN(count) || count <= 0) return;

    try {
        await axios.post('/project/flags/insert_n', {
            left_idx: idx,
            count: count
        });
        fetchStatus();
        onClose();
    } catch (e) {
        console.error(e);
    }
  };

  const hasNext = idx < flags.length - 1;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface border border-grid rounded-lg shadow-2xl w-full max-w-sm overflow-hidden text-text flex flex-col isolation-auto"
           style={{ backgroundColor: 'var(--color-surface)' }}
           onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-grid font-bold text-sm uppercase tracking-widest opacity-80 flex justify-between items-center">
            <span>Edit Flag</span>
            <span className="font-mono text-[10px] opacity-40">#{idx}</span>
        </div>
        <div className="p-4 space-y-4">
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Name</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent text-sm" />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Time (s)</label>
                <input type="number" step="0.001" min="0" max={duration} value={t} onChange={(e) => setT(parseFloat(e.target.value))}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent text-sm font-mono" />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">Subdivision</label>
                <input type="number" min="0" max="32" value={subdivision} onChange={(e) => setSubdivision(parseInt(e.target.value))}
                       className="w-full bg-background border border-grid rounded p-2 outline-none focus:border-accent text-sm" />
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
            {hasNext && (
                <button onClick={handleInsertN} className="w-full py-2 rounded bg-white/5 hover:bg-white/10 text-xs font-bold transition-colors border border-grid">
                    Insert N flags between this and next
                </button>
            )}
        </div>
        <div className="p-4 border-t border-grid flex items-center justify-between gap-2">
            <button onClick={handleDelete} className="px-4 py-2 rounded bg-red-600/20 hover:bg-red-600/40 text-red-500 text-xs font-bold transition-colors">Delete</button>
            <div className="flex items-center gap-2">
                <button onClick={onClose} className="px-4 py-2 rounded hover:bg-white/5 text-xs transition-colors font-bold">Cancel</button>
                <button onClick={handleSave} className="px-4 py-2 rounded bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">Save</button>
            </div>
        </div>
      </div>
    </div>
  );
};
