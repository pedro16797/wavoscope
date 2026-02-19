import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { useStore, API_BASE } from '../store/useStore';
import { getChordMidiNotes, midiToFreq, freqToMidi } from '../store/utils';
import axios from 'axios';

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const WHITE_KEYS = new Set([0, 2, 4, 5, 7, 9, 11]);

export const Spectrum: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    loaded, position, currentTheme, themes, fft_window, octave_shift, spectrum_keys,
    filter_enabled, filter_low_enabled, filter_high_enabled, filter_low_hz, filter_high_hz, updateFilter,
    playTone: playToneStore, stopAllTones
  } = useStore();
  const [data, setData] = useState<{ freqs: number[], db: number[] }>({ freqs: [], db: [] });
  const [size, setSize] = useState({ width: 0, height: 0 });
  const inFlightRef = useRef(false);
  const pendingRef = useRef<{ position: number, window: number, low: number, high: number, width: number } | null>(null);

  const baseMidi = 48 + octave_shift * 12;
  const range = {
    low: midiToFreq(baseMidi),
    high: midiToFreq(baseMidi + spectrum_keys)
  };

  const updateSize = useCallback(() => {
    if (containerRef.current && canvasRef.current) {
      const dpr = window.devicePixelRatio || 1;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      canvasRef.current.width = w * dpr;
      canvasRef.current.height = h * dpr;
      setSize({ width: w, height: h });
    }
  }, []);

  useEffect(() => {
    const observer = new ResizeObserver(updateSize);
    if (containerRef.current) observer.observe(containerRef.current);
    updateSize();
    return () => observer.disconnect();
  }, [updateSize]);

  useEffect(() => {
    if (!loaded) return;

    const fetchSpectrum = async (p: number, w: number, low: number, high: number, width: number) => {
        if (inFlightRef.current) {
            pendingRef.current = { position: p, window: w, low, high, width };
            return;
        }

        inFlightRef.current = true;
        try {
            const res = await axios.get(`${API_BASE}/audio/spectrum`, {
                params: {
                    position: p,
                    window: w,
                    low_hz: low,
                    high_hz: high,
                    width: width
                }
            });
            setData(res.data);
        } catch (e) {
            console.error(e);
        } finally {
            inFlightRef.current = false;
            if (pendingRef.current) {
                const next = pendingRef.current;
                pendingRef.current = null;
                fetchSpectrum(next.position, next.window, next.low, next.high, next.width);
            }
        }
    };

    fetchSpectrum(position, fft_window, range.low, range.high, size.width || 1000);
  }, [loaded, position, range.low, range.high, fft_window, size.width]);

  const harmony_flags = useStore(state => state.harmony_flags);
  const activeChordNotes = useMemo(() => {
    // Find the last flag before or at the current position
    let activeFlag = null;
    for (const f of harmony_flags) {
        if (f.t <= position) activeFlag = f;
        else break;
    }
    return activeFlag ? getChordMidiNotes(activeFlag.c) : [];
  }, [position, harmony_flags]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const theme = themes[currentTheme];
    if (!canvas || !theme?.spectrum || size.width === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.width, size.height);
    const h = size.height;
    const w = size.width;
    const spanLog = Math.max(Math.log2(range.high / range.low), 1e-3);
    const xScale = w / spanLog;

    const firstMidi = Math.round(freqToMidi(range.low));
    for (let midi = firstMidi; midi < firstMidi + spectrum_keys; midi++) {
        const hz = midiToFreq(midi);
        const x = Math.log2(hz / range.low) * xScale;
        if (x < 0 || x > w) continue;

        const isActive = activeChordNotes.some(n => n % 12 === midi % 12);

        ctx.strokeStyle = WHITE_KEYS.has(midi % 12) ? (theme.keyWhite || '#fff') : (theme.keyBlack || '#333');
        ctx.globalAlpha = isActive ? 0.9 : 0.4;
        ctx.lineWidth = isActive ? 4 : 2;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();

        if (isActive) {
            ctx.fillStyle = theme.accent;
            ctx.globalAlpha = 0.2;
            ctx.fillRect(x - 2, 0, 4, h);
        }

        ctx.globalAlpha = 0.8;
        ctx.fillStyle = theme.text;
        ctx.font = '10px sans-serif';
        ctx.fillText(`${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`, x + 4, 12);
    }

    const xLow = Math.log2(filter_low_hz / range.low) * xScale;
    const xHigh = Math.log2(filter_high_hz / range.low) * xScale;

    // Shaded areas
    ctx.fillStyle = '#000';
    ctx.globalAlpha = 0.5;
    if (filter_low_enabled && xLow > 0) ctx.fillRect(0, 0, xLow, h);
    if (filter_high_enabled && xHigh < w) ctx.fillRect(xHigh, 0, w - xHigh, h);

    // Low Cutoff Handle
    if (xLow >= 0 && xLow <= w) {
        ctx.strokeStyle = theme.accent;
        ctx.setLineDash(filter_low_enabled ? [] : [5, 5]);
        ctx.lineWidth = 2;
        ctx.globalAlpha = filter_low_enabled ? 0.8 : 0.3;
        ctx.beginPath(); ctx.moveTo(xLow, 0); ctx.lineTo(xLow, h); ctx.stroke();

        ctx.fillStyle = theme.accent;
        ctx.globalAlpha = filter_low_enabled ? 1.0 : 0.4;
        ctx.fillRect(xLow - 6, h - 30, 12, 30);
        ctx.fillStyle = theme.text;
        ctx.globalAlpha = filter_low_enabled ? 1.0 : 0.6;
        ctx.font = 'bold 10px sans-serif';
        ctx.fillText('LOW', xLow + 8, h - 10);
    }

    // High Cutoff Handle
    if (xHigh >= 0 && xHigh <= w) {
        ctx.strokeStyle = theme.accent;
        ctx.setLineDash(filter_high_enabled ? [] : [5, 5]);
        ctx.lineWidth = 2;
        ctx.globalAlpha = filter_high_enabled ? 0.8 : 0.3;
        ctx.beginPath(); ctx.moveTo(xHigh, 0); ctx.lineTo(xHigh, h); ctx.stroke();

        ctx.fillStyle = theme.accent;
        ctx.globalAlpha = filter_high_enabled ? 1.0 : 0.4;
        ctx.fillRect(xHigh - 6, h - 30, 12, 30);
        ctx.fillStyle = theme.text;
        ctx.globalAlpha = filter_high_enabled ? 1.0 : 0.6;
        ctx.font = 'bold 10px sans-serif';
        ctx.fillText('HIGH', xHigh - 35, h - 10);
    }
    ctx.setLineDash([]);
    ctx.globalAlpha = 1.0;

    if (data.freqs.length > 0) {
        ctx.globalAlpha = 1;
        ctx.strokeStyle = theme.spectrum;
        ctx.lineWidth = 1;

        const minDb = Math.min(...data.db);
        const maxDb = Math.max(...data.db);
        const spanDb = Math.max(maxDb - minDb, 1e-3);

        ctx.beginPath();
        data.freqs.forEach((f, i) => {
            const px = Math.log2(f / range.low) * xScale;
            // Draw with a small vertical margin to avoid clipping at the edges
            const py = (h * 0.95) - ((data.db[i] - minDb) / spanDb) * (h * 0.9);
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });
        ctx.stroke();
    }
  }, [data, range.low, range.high, themes, currentTheme, spectrum_keys, size, activeChordNotes, filter_enabled, filter_low_enabled, filter_high_enabled, filter_low_hz, filter_high_hz]);

  const lastToneRef = useRef<number>(0);
  const currentHzRef = useRef<number>(0);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only handle left-click
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const spanLog = Math.log2(range.high / range.low);
    const xScale = rect.width / spanLog;

    const xLow = Math.log2(filter_low_hz / range.low) * xScale;
    const xHigh = Math.log2(filter_high_hz / range.low) * xScale;

    let dragging: 'low' | 'high' | 'tone' = 'tone';

    if (Math.abs(x - xLow) < 20) dragging = 'low';
    else if (Math.abs(x - xHigh) < 20) dragging = 'high';

    const onMouseMove = (moveEvent: MouseEvent) => {
        const mx = moveEvent.clientX - rect.left;
        const hz = range.low * Math.pow(2, (mx * spanLog / rect.width));

        if (dragging === 'low') {
            updateFilter({ low_hz: hz });
        } else if (dragging === 'high') {
            updateFilter({ high_hz: hz });
        } else {
            auditionTone(moveEvent.clientX);
        }
    };

    const auditionTone = (clientX: number) => {
        const x = clientX - rect.left;
        const spanLog = Math.log2(range.high / range.low);
        const hz = range.low * Math.pow(2, (x * spanLog / rect.width));

        // Round to nearest MIDI note frequency for cleaner dragging
        const midi = Math.round(freqToMidi(hz));
        const snappedHz = midiToFreq(midi);

        if (snappedHz === currentHzRef.current) return;

        const now = Date.now();
        if (now - lastToneRef.current > 30) {
            if (currentHzRef.current > 0) {
                playToneStore(currentHzRef.current, 'stop');
            }
            playToneStore(snappedHz, 'start');
            currentHzRef.current = snappedHz;
            lastToneRef.current = now;
        }
    };

    if (dragging === 'tone') {
        auditionTone(e.clientX);
    }

    const onMouseUp = () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        if (dragging === 'tone') {
            stopAllTones();
            currentHzRef.current = 0;
        }
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = e.clientX - rect.left;
    const spanLog = Math.log2(range.high / range.low);
    const xScale = rect.width / spanLog;
    const hz = range.low * Math.pow(2, (x * spanLog / rect.width));

    const xLow = Math.log2(filter_low_hz / range.low) * xScale;
    const xHigh = Math.log2(filter_high_hz / range.low) * xScale;

    // Check if clicking on a handle area
    if (Math.abs(x - xLow) < 20) {
        updateFilter({ low_enabled: !filter_low_enabled, enabled: true });
        return;
    }
    if (Math.abs(x - xHigh) < 20) {
        updateFilter({ high_enabled: !filter_high_enabled, enabled: true });
        return;
    }

    // Otherwise, place nearest handle here and enable it
    if (Math.abs(x - xLow) < Math.abs(x - xHigh)) {
        updateFilter({ low_hz: hz, low_enabled: true, enabled: true });
    } else {
        updateFilter({ high_hz: hz, high_enabled: true, enabled: true });
    }
  };

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden select-none"
         onMouseDown={handleMouseDown}
         onContextMenu={handleContextMenu}>
        <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
};
