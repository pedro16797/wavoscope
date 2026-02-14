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
  const { loaded, position, currentTheme, themes } = useStore();
  const [data, setData] = useState<{ freqs: number[], db: number[] }>({ freqs: [], db: [] });
  const [range] = useState({ low: midiToFreq(48), high: midiToFreq(84) }); // C2 to C5

  const theme = themes[currentTheme] || {};

  const updateSize = useCallback(() => {
    if (containerRef.current && canvasRef.current) {
      canvasRef.current.width = containerRef.current.clientWidth;
      canvasRef.current.height = containerRef.current.clientHeight;
    }
  }, []);

  useEffect(() => {
    window.addEventListener('resize', updateSize);
    updateSize();
    return () => window.removeEventListener('resize', updateSize);
  }, [updateSize]);

  useEffect(() => {
    if (!loaded) return;
    const fetchSpectrum = async () => {
        try {
            const res = await axios.get(`http://127.0.0.1:8000/audio/spectrum`, {
                params: {
                    position,
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
  }, [loaded, position, range]);

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

    // Draw piano-key grid
    const firstMidi = Math.round(freqToMidi(range.low));
    const visibleKeys = 37; // Default from Qt version
    for (let midi = firstMidi; midi < firstMidi + visibleKeys; midi++) {
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

    // Draw spectrum line
    if (data.freqs.length > 0) {
        ctx.globalAlpha = 1;
        ctx.strokeStyle = theme.spectrum;
        ctx.lineWidth = 1;

        // Simple normalization for visualization
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
  }, [data, range, theme]);

  const handleMouseDown = (e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;

    const playTone = (clientX: number) => {
        const x = clientX - rect.left;
        const spanLog = Math.log2(range.high / range.low);
        const hz = range.low * Math.pow(2, (x * spanLog / rect.width));
        axios.post(`http://127.0.0.1:8000/playback/tone`, { freq: hz, action: 'start' });
    };

    playTone(e.clientX);

    const onMouseMove = (moveEvent: MouseEvent) => {
        playTone(moveEvent.clientX);
    };

    const onMouseUp = () => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        axios.post(`http://127.0.0.1:8000/playback/tone`, { action: 'stop' });
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
