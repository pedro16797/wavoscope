import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react';
import { useStore, API_BASE, getChordMidiNotes } from '../store/useStore';
import axios from 'axios';

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const WHITE_KEYS = new Set([0, 2, 4, 5, 7, 9, 11]);

const midiToFreq = (midi: number) => 440.0 * Math.pow(2, (midi - 69) / 12);
const freqToMidi = (freq: number) => 12 * Math.log2(freq / 440) + 69;

export const Spectrum: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { loaded, position, currentTheme, themes, fft_window, octave_shift, spectrum_keys } = useStore();
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

  const activeChordNotes = useMemo(() => {
    const { harmony_flags } = useStore.getState();
    // Find the last flag before or at the current position
    let activeFlag = null;
    for (const f of harmony_flags) {
        if (f.t <= position) activeFlag = f;
        else break;
    }
    return activeFlag ? getChordMidiNotes(activeFlag.chord) : [];
  }, [position, useStore.getState().harmony_flags]);

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
  }, [data, range.low, range.high, themes, currentTheme, spectrum_keys, size, activeChordNotes]);

  const lastToneRef = useRef<number>(0);
  const currentHzRef = useRef<number>(0);

  const handleMouseDown = (e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const playTone = (clientX: number) => {
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
                axios.post(`${API_BASE}/playback/tone`, { freq: currentHzRef.current, action: 'stop' });
            }
            axios.post(`${API_BASE}/playback/tone`, { freq: snappedHz, action: 'start' });
            currentHzRef.current = snappedHz;
            lastToneRef.current = now;
        }
    };

    playTone(e.clientX);

    const onMouseMove = (moveEvent: MouseEvent) => {
        playTone(moveEvent.clientX);
    };

    const onMouseUp = () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        axios.post(`${API_BASE}/playback/tone`, { action: 'stop' });
        currentHzRef.current = 0;
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden select-none"
         onMouseDown={handleMouseDown}>
        <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
};
