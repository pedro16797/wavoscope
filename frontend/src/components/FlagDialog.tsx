import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import type { Flag } from '../store/types';
import { Tooltip } from './Tooltip';

export const FlagDialog: React.FC<{ idx: number; flag: Flag; onClose: () => void }> = ({ idx, flag, onClose }) => {
  const { t } = useTranslation();
  const { duration, flags, removeFlag, updateFlag, insertNFlags } = useStore();

  const [name, setName] = useState(flag?.n || '');
  const [time, setTime] = useState(flag?.t || 0);
  const [subdivision, setSubdivision] = useState(flag?.div || 0);
  const [sectionStart, setSectionStart] = useState(flag?.s || false);
  const [shaded, setShaded] = useState(flag?.divshade || false);

  if (!flag) {
    console.error("FlagDialog opened but flag is missing at index", idx);
    onClose();
    return null;
  }

  const handleSave = async () => {
    await updateFlag(idx, {
        t: time,
        n: name,
        div: subdivision,
        type: flag.type,
        s: sectionStart,
        divshade: shaded
    });
    onClose();
  };

  const handleDelete = async () => {
    await removeFlag(idx);
    onClose();
  };

  const handleInsertN = async () => {
    const countStr = prompt(t('flag.insert_prompt'), "3");
    if (!countStr) return;
    const count = parseInt(countStr);
    if (isNaN(count) || count <= 0) return;

    await insertNFlags(idx, count);
    onClose();
  };

  const hasNext = idx < flags.length - 1;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] shadow-2xl w-full max-w-sm overflow-hidden text-text flex flex-col isolation-auto"
           style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}
           onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b-[var(--ui-border)] border-grid font-bold text-sm uppercase tracking-widest opacity-80 flex justify-between items-center bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>
            <span>{t('flag.edit_title')}</span>
            <span className="font-mono text-[10px] opacity-40">#{idx}</span>
        </div>
        <div className="p-4 space-y-4">
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('flag.name')}</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                       className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm text-text"
                       style={{ borderWidth: 'var(--ui-border)' }} />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('flag.time')}</label>
                <input type="number" step="0.001" min="0" max={duration} value={time} onChange={(e) => setTime(parseFloat(e.target.value))}
                       className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm font-mono text-text"
                       style={{ borderWidth: 'var(--ui-border)' }} />
            </div>
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('flag.subdivisions')}</label>
                <input type="number" min="0" max="32" value={subdivision} onChange={(e) => setSubdivision(parseInt(e.target.value))}
                       className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm text-text"
                       style={{ borderWidth: 'var(--ui-border)' }} />
            </div>
            <div className="flex items-center gap-4 py-2">
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={sectionStart} onChange={(e) => setSectionStart(e.target.checked)} className="accent-accent" />
                    <span className="text-xs">{t('flag.section_start')}</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={shaded} onChange={(e) => setShaded(e.target.checked)} className="accent-accent" />
                    <span className="text-xs">{t('flag.shaded')}</span>
                </label>
            </div>
            {hasNext && (
                <button onClick={handleInsertN} className="w-full py-2 rounded-[var(--ui-radius)] bg-white/5 hover:bg-white/10 text-xs font-bold transition-colors border-[var(--ui-border)] border-grid"
                        style={{ borderWidth: 'var(--ui-border)' }}>
                    {t('flag.insert_n')}
                </button>
            )}
        </div>
        <div className="p-4 border-t-[var(--ui-border)] border-grid flex items-center justify-between gap-2 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderTopWidth: 'var(--ui-border)' }}>
            <Tooltip content={t('common.delete')} shortcut={t('keys.delete')}>
                <button onClick={handleDelete} className="px-4 py-2 rounded-[var(--ui-radius)] bg-red-600/20 hover:bg-red-600/40 text-red-500 text-xs font-bold transition-colors">{t('common.delete')}</button>
            </Tooltip>
            <div className="flex items-center gap-2">
                <Tooltip content={t('common.cancel')}>
                    <button onClick={onClose} className="px-4 py-2 rounded-[var(--ui-radius)] hover:bg-white/5 text-xs transition-colors font-bold">{t('common.cancel')}</button>
                </Tooltip>
                <Tooltip content={t('common.save')} shortcut={t('keys.enter')}>
                    <button onClick={handleSave} className="px-4 py-2 rounded-[var(--ui-radius)] bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">{t('common.save')}</button>
                </Tooltip>
            </div>
        </div>
      </div>
    </div>
  );
};
