import React, { useEffect, useRef, useState } from 'react';
import { useStore } from './store';
import { useTheme } from './ThemeContext';

const API_URL = 'http://127.0.0.1:8000';
const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const WHITE_KEYS = new Set([0, 2, 4, 5, 7, 9, 11]);

function midiToFreq(midi: number) {
  return 440.0 * Math.pow(2, (midi - 69) / 12);
}

interface SpectrumData {
  freqs: number[];
  db: number[];
  t: number;
  window: number;
}

export const SpectrogramViewer: React.FC<{ windowSize: number }> = ({ windowSize }) => {
  const store = useStore();
  const { theme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [spectrumData, setSpectrumData] = useState<SpectrumData | null>(null);

  const lowMidi = 48; // C2
  const visibleKeys = 37;
  const highMidi = lowMidi + visibleKeys - 1;
  const lowHz = midiToFreq(lowMidi);
  const highHz = midiToFreq(highMidi);

  useEffect(() => {
    const fetchSpectrum = async () => {
      if (!store.isPlaying && spectrumData && spectrumData.t === store.position && spectrumData.window === windowSize) return;

      try {
        const res = await fetch(`${API_URL}/spectrum?t=${store.position}&window=${windowSize}&low=${lowHz}&high=${highHz}&width=1000`);
        if (res.ok) {
          const data = await res.json();
          setSpectrumData({ ...data, t: store.position, window: windowSize });
        }
      } catch (e) {}
    };

    const interval = setInterval(fetchSpectrum, 50);
    return () => clearInterval(interval);
  }, [store.position, store.isPlaying, windowSize]);

  useEffect(() => {
    if (!canvasRef.current || !spectrumData || !theme) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const w = canvas.width;
    const h = canvas.height;
    const spanLog = Math.log2(highHz / lowHz);
    const xScale = w / spanLog;

    // Piano-key grid
    for (let midi = lowMidi; midi <= highMidi; midi++) {
      const hz = midiToFreq(midi);
      const x = Math.log2(hz / lowHz) * xScale;

      ctx.strokeStyle = WHITE_KEYS.has(midi % 12) ? theme.keyWhite : theme.keyBlack;
      ctx.globalAlpha = 0.5;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();

      ctx.globalAlpha = 1.0;
      ctx.fillStyle = theme.text;
      ctx.font = '10px sans-serif';
      ctx.fillText(`${NOTE_NAMES[midi % 12]}${Math.floor((midi - 12) / 12)}`, x + 2, 12);
    }

    // Spectrum line
    const { freqs, db } = spectrumData;
    if (freqs.length > 0) {
      // Find min/max db for normalization (Qt used percentiles, we'll simplify or use same)
      const sortedDb = [...db].sort((a, b) => a - b);
      const lowDb = sortedDb[Math.floor(sortedDb.length * 0.01)];
      const highDb = sortedDb[Math.floor(sortedDb.length * 0.99)];
      const spanDb = Math.max(1.05 * highDb - lowDb, 1e-3);

      ctx.strokeStyle = theme.spectrum;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let i = 0; i < freqs.length; i++) {
        const px = Math.log2(freqs[i] / lowHz) * xScale;
        const py = h - ((db[i] - lowDb) / spanDb) * h;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
    }
  }, [spectrumData, theme]);

  return (
    <div className="bg-surface rounded-lg p-2 h-40 relative">
      <canvas ref={canvasRef} width={1000} height={160} className="w-full h-full" />
    </div>
  );
};
