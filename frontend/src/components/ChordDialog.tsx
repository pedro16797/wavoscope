import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import type { HarmonyFlag, Chord } from '../store/types';
import { formatChord, getChordMidiNotes, midiToFreq } from '../store/utils';
import { Volume2 } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface ChordDialogProps {
  idx: number;
  flag: HarmonyFlag;
  onClose: () => void;
}

const ROOTS = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
const ACCIDENTALS = ['', '#', 'b'];
const QUALITIES = ['', 'm', 'dim', 'aug', 'sus2', 'sus4'];
const EXTENSIONS = ['', '7', '9', '11', '13'];
const ALTERATIONS = ['b5', '#5', 'b9', '#9', '#11', 'b13'];
const ADDITIONS = ['add9', 'add11', 'add13'];

export const ChordDialog: React.FC<ChordDialogProps> = ({ idx, flag, onClose }) => {
  const { t } = useTranslation();
  const { updateHarmonyFlag, removeHarmonyFlag, duration, playTone, stopAllTones } = useStore();
  const [chord, setChord] = useState<Chord>(flag.c);
  const [time, setTime] = useState(flag.t);
  const [chordText, setChordText] = useState(formatChord(flag.c));

  const handleTextChange = (text: string) => {
    setChordText(text);
    const newChord: Chord = { ...chord };

    // Regex to pull apart the string
    // 1: Root, 2: Accidental, 3: Quality, 4: Extension, 5: Rest (Alterations, Additions, Bass)
    const mainRegex = /^([A-G])([#b]?)(m|dim|aug|sus2|sus4|M?)(7|9|11|13|)?(.*)$/;
    const match = text.match(mainRegex);

    if (match) {
        newChord.r = match[1];
        newChord.ca = match[2];
        newChord.q = match[3] === 'M' ? '' : (match[3] || '');
        newChord.ext = match[4] || '';

        let rest = match[5];

        // Parse Bass
        const bassMatch = rest.match(/\/([A-G])([#b]?)$/);
        if (bassMatch) {
            newChord.b = bassMatch[1];
            newChord.ba = bassMatch[2];
            rest = rest.replace(/\/([A-G])([#b]?)$/, '');
        } else {
            newChord.b = '';
            newChord.ba = '';
        }

        // Parse Alterations
        const alts: string[] = [];
        ALTERATIONS.forEach(a => {
            if (rest.includes(a)) {
                alts.push(a);
                rest = rest.replace(a, '');
            }
        });
        newChord.alt = alts;

        // Parse Additions
        const adds: string[] = [];
        ADDITIONS.forEach(a => {
            if (rest.includes(a)) {
                adds.push(a);
                rest = rest.replace(a, '');
            }
        });
        newChord.add = adds;

        // Only update the chord object if we have a clean parse or at least a root
        // This avoids resetting the quality/extension while the user is typing "dim" for example.
        setChord(newChord);
    }
  };

  const handleBlur = () => {
    setChordText(formatChord(chord));
  };

  const updateChordFromSelectors = (updates: Partial<Chord>) => {
    const nextChord = { ...chord, ...updates };
    setChord(nextChord);
    setChordText(formatChord(nextChord));
  };

  const handleSave = () => {
    updateHarmonyFlag(idx, time, chord);
    onClose();
  };

  const handleDelete = () => {
    removeHarmonyFlag(idx);
    onClose();
  };

  const toggleAlteration = (altVal: string) => {
    const newAlts = chord.alt.includes(altVal)
        ? chord.alt.filter(a => a !== altVal)
        : [...chord.alt, altVal];
    updateChordFromSelectors({ alt: newAlts });
  };

  const toggleAddition = (addVal: string) => {
    const newAdds = chord.add.includes(addVal)
        ? chord.add.filter(a => a !== addVal)
        : [...chord.add, addVal];
    updateChordFromSelectors({ add: newAdds });
  };

  const handlePlayStart = () => {
    const midis = getChordMidiNotes(chord);
    midis.forEach(m => {
        playTone(midiToFreq(m), 'start');
    });
  };

  const handlePlayStop = () => {
    stopAllTones();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-surface border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] shadow-2xl w-full max-w-md overflow-hidden text-text flex flex-col isolation-auto"
           style={{ backgroundColor: 'var(--color-surface)', borderWidth: 'var(--ui-border)' }}
           onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b-[var(--ui-border)] border-grid font-bold text-sm uppercase tracking-widest opacity-80 flex justify-between items-center bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderBottomWidth: 'var(--ui-border)' }}>
            <span>{t('chord.edit_title')}</span>
            <span className="font-mono text-[10px] opacity-40">#{idx}</span>
        </div>

        <div className="p-4 space-y-4">
            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.notation')}</label>
                <div className="flex gap-2">
                    <input type="text" value={chordText}
                           autoFocus
                           onFocus={e => e.target.select()}
                           onChange={(e) => handleTextChange(e.target.value)}
                           onBlur={handleBlur}
                           onKeyDown={e => e.key === 'Enter' && (handleBlur(), handleSave())}
                           className="flex-1 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-3 outline-none focus:border-accent text-xl font-bold text-accent text-center"
                           style={{ borderWidth: 'var(--ui-border)' }} />
                    <Tooltip content={t('chord.audition')}>
                        <button
                            onMouseDown={handlePlayStart}
                            onMouseUp={handlePlayStop}
                            onMouseLeave={handlePlayStop}
                            className="px-4 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] hover:bg-white/5 text-accent transition-colors flex items-center justify-center group active:scale-95"
                            style={{ borderWidth: 'var(--ui-border)' }}
                        >
                            <Volume2 size={20} className="group-active:scale-110 transition-transform" />
                        </button>
                    </Tooltip>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.root')}</label>
                    <div className="flex gap-1">
                        <select value={chord.r} onChange={e => updateChordFromSelectors({ r: e.target.value })}
                                className="flex-1 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {ROOTS.map(r => <option key={r} value={r}>{r}</option>)}
                        </select>
                        <select value={chord.ca} onChange={e => updateChordFromSelectors({ ca: e.target.value })}
                                className="w-12 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {ACCIDENTALS.map(a => <option key={a} value={a}>{a || '♮'}</option>)}
                        </select>
                    </div>
                </div>
                <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.quality_ext')}</label>
                    <div className="flex gap-1">
                        <select value={chord.q} onChange={e => updateChordFromSelectors({ q: e.target.value })}
                                className="flex-1 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {QUALITIES.map(q => <option key={q} value={q}>{q || 'M'}</option>)}
                        </select>
                        <select value={chord.ext} onChange={e => updateChordFromSelectors({ ext: e.target.value })}
                                className="w-14 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {EXTENSIONS.map(ex => <option key={ex} value={ex}>{ex || t('chord.triad')}</option>)}
                        </select>
                    </div>
                </div>
            </div>

            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.alterations')}</label>
                <div className="flex flex-wrap gap-2">
                    {ALTERATIONS.map(altVal => (
                        <button key={altVal} onClick={() => toggleAlteration(altVal)}
                                className={`px-2 py-1 rounded-[var(--ui-radius)] text-[10px] font-bold border-[var(--ui-border)] transition-colors ${chord.alt.includes(altVal) ? 'bg-accent text-background border-accent' : 'bg-white/5 border-grid hover:bg-white/10'}`}
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {altVal}
                        </button>
                    ))}
                </div>
            </div>

            <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.added_tones')}</label>
                <div className="flex flex-wrap gap-2">
                    {ADDITIONS.map(addVal => (
                        <button key={addVal} onClick={() => toggleAddition(addVal)}
                                className={`px-2 py-1 rounded-[var(--ui-radius)] text-[10px] font-bold border-[var(--ui-border)] transition-colors ${chord.add.includes(addVal) ? 'bg-accent text-background border-accent' : 'bg-white/5 border-grid hover:bg-white/10'}`}
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {addVal}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                 <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.bass')}</label>
                    <div className="flex gap-1">
                        <select value={chord.b} onChange={e => updateChordFromSelectors({ b: e.target.value })}
                                className="flex-1 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            <option value="">{t('common.none')}</option>
                            {ROOTS.map(r => <option key={r} value={r}>{r}</option>)}
                        </select>
                        <select value={chord.ba} onChange={e => updateChordFromSelectors({ ba: e.target.value })}
                                className="w-12 bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 text-sm outline-none text-text"
                                style={{ borderWidth: 'var(--ui-border)' }}>
                            {ACCIDENTALS.map(a => <option key={a} value={a}>{a || '♮'}</option>)}
                        </select>
                    </div>
                </div>
                <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold opacity-50">{t('chord.time')}</label>
                    <input type="number" step="0.001" min="0" max={duration} value={time} onChange={(e) => setTime(parseFloat(e.target.value))}
                           className="w-full bg-background border-[var(--ui-border)] border-grid rounded-[var(--ui-radius)] p-2 outline-none focus:border-accent text-sm font-mono text-text"
                           style={{ borderWidth: 'var(--ui-border)' }} />
                </div>
            </div>
        </div>

        <div className="p-4 border-t-[var(--ui-border)] border-grid flex items-center justify-between gap-2 bg-surface"
             style={{ backgroundColor: 'var(--color-surface)', borderTopWidth: 'var(--ui-border)' }}>
            <button onClick={handleDelete} className="px-4 py-2 rounded-[var(--ui-radius)] bg-red-600/20 hover:bg-red-600/40 text-red-500 text-xs font-bold transition-colors">{t('common.delete')}</button>
            <div className="flex items-center gap-2">
                <button onClick={onClose} className="px-4 py-2 rounded-[var(--ui-radius)] hover:bg-white/5 text-xs transition-colors font-bold">{t('common.cancel')}</button>
                <button onClick={handleSave} className="px-4 py-2 rounded-[var(--ui-radius)] bg-accent text-background text-xs font-bold transition-colors shadow-lg active:scale-95">{t('common.save')}</button>
            </div>
        </div>
      </div>
    </div>
  );
};
