import React, { useState, useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { Tooltip } from './Tooltip';
import { Activity } from 'lucide-react';

export const TempoDisplay: React.FC = () => {
  const { t } = useTranslation();
  const { position, flags, time_signature, ui_scale } = useStore();

  const [taps, setTaps] = useState<number[]>([]);
  const [isTapping, setIsTapping] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const measureBpm = useMemo(() => {
    const rhythmFlags = flags.filter(f => (f.type || 'rhythm') === 'rhythm');
    if (rhythmFlags.length === 0) return 120;

    // Clone and ensure start at 0
    const rFlags = [...rhythmFlags];
    if (rFlags[0].t > 0.05) {
        let firstDiv = rFlags[0].div;
        if (firstDiv === 0) {
            firstDiv = time_signature.numerator;
        }
        rFlags.unshift({ t: 0, div: firstDiv, type: 'rhythm' } as any);
    }

    let start_t = 0;
    let end_t = 0;
    let subdiv = time_signature.numerator;

    for (let i = 0; i < rFlags.length; i++) {
        if (rFlags[i].t <= position + 0.001) { // Small epsilon for floating point
            start_t = rFlags[i].t;
            if (i + 1 < rFlags.length) {
                end_t = rFlags[i+1].t;
            } else {
                const prev_interval = i > 0 ? (rFlags[i].t - rFlags[i-1].t) : 2.0;
                end_t = start_t + (prev_interval > 0.1 ? prev_interval : 2.0);
            }

            let s = rFlags[i].div;
            if (s === 0) {
                for (let j = i; j >= 0; j--) {
                    if (rFlags[j].div !== 0) {
                        s = rFlags[j].div;
                        break;
                    }
                }
                if (s === 0) s = time_signature.numerator;
            }
            subdiv = s;
        } else {
            break;
        }
    }

    const duration = Math.max(0.1, end_t - start_t);
    return (subdiv * 60.0) / duration;
  }, [position, flags, time_signature]);

  const tappedBpm = useMemo(() => {
    if (taps.length < 2) return null;
    const intervals = [];
    for (let i = 1; i < taps.length; i++) {
        intervals.push(taps[i] - taps[i-1]);
    }
    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    if (avgInterval <= 0) return null;
    return 60000 / avgInterval;
  }, [taps]);

  const handleTap = (e: React.MouseEvent) => {
    e.stopPropagation();
    const now = Date.now();

    setTaps(prev => {
        const last = prev[prev.length - 1];
        // If last tap was more than 3 seconds ago, start fresh
        if (last && now - last > 3000) return [now];
        const next = [...prev, now];
        if (next.length > 12) return next.slice(1); // Keep last 12 taps for better average
        return next;
    });

    setIsTapping(true);

    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
        setIsTapping(false);
        setTaps([]);
    }, 3000);
  };

  const displayBpm = isTapping && tappedBpm !== null ? tappedBpm : measureBpm;

  return (
    <Tooltip content={t('views.tap_tempo')}>
      <button
        onClick={handleTap}
        className={`flex items-center gap-1 px-2 py-0.5 rounded transition-colors hover:bg-white/10 ${isTapping ? 'text-accent' : ''}`}
        style={{ color: 'inherit' }}
      >
        <Activity size={12 * ui_scale} className={isTapping ? 'animate-pulse' : 'opacity-70'} />
        <span className="font-mono font-bold" style={{ fontSize: 10 * ui_scale }}>
            {t('views.tempo', { bpm: displayBpm.toFixed(1) }).split(' ')[0]}
        </span>
        <span className="opacity-50 ml-0.5" style={{ fontSize: 8 * ui_scale }}>
            {t('views.tempo', { bpm: displayBpm.toFixed(1) }).split(' ')[1] || 'BPM'}
        </span>
      </button>
    </Tooltip>
  );
};
