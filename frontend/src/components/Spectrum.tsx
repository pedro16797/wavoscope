import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useStore } from '../store/useStore';
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

  const theme = themes[currentTheme] || {};

  const baseMidi = 48 + octave_shift * 12;
  const range = {
    low: midiToFreq(baseMidi),
    high: midiToFreq(baseMidi + spectrum_keys)
  };

  const updateSize = useCallback(() => {
    if (containerRef.current && canvasRef.current) {
      canvasRef.current.width = containerRef.current.clientWidth;
      canvasRef.current.height = containerRef.current.clientHeight;
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
    const fetchSpectrum = async () => {
        try {
            const res = await axios.get(`/audio/spectrum`, {
                params: {
                    position,
                    window: fft_window,
                    low_hz: range.low,
                    high_hz: range.high,
                    width: canvasRef.current?.width || 1000
                }
            });
            setData(res.data);
        } catch (e) {
            console.error(e);
        }
    };
    fetchSpectrum();
  }, [loaded, position, range.low, range.high, fft_window]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !theme.spectrum) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const h = canvas.height;
    const w = canvas.width;
    const spanLog = Math.max(Math.log2(range.high / range.low), 1e-3);
    const xScale = w / spanLog;

    const firstMidi = Math.round(freqToMidi(range.low));
    for (let midi = firstMidi; midi < firstMidi + spectrum_keys; midi++) {
        const hz = midiToFreq(midi);
        const x = Math.log2(hz / range.low) * xScale;
        if (x < 0 || x > w) continue;

        ctx.strokeStyle = WHITE_KEYS.has(midi % 12) ? (theme.keyWhite || '#fff') : (theme.keyBlack || '#333');
        ctx.globalAlpha = 0.5;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();

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
            const py = h - ((data.db[i] - minDb) / spanDb) * h;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        });
        ctx.stroke();
    }
  }, [data, range.low, range.high, theme, spectrum_keys]);

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
                axios.post(`/playback/tone`, { freq: currentHzRef.current, action: 'stop' });
            }
            axios.post(`/playback/tone`, { freq: snappedHz, action: 'start' });
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
        axios.post(`/playback/tone`, { action: 'stop' });
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
