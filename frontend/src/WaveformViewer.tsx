import React, { useEffect, useRef, useState } from 'react';
import { useStore } from './store';
import { useTheme } from './ThemeContext';

const API_URL = 'http://127.0.0.1:8000';

export const WaveformViewer: React.FC = () => {
  const store = useStore();
  const { theme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [bars, setBars] = useState<[number, number, number][]>([]);
  const isDragging = useRef(false);
  const lastX = useRef(0);

  const fetchWaveform = async () => {
    if (store.duration === 0) return;
    // Actually zoom in Qt was pixels/sample.
    // end_sec = start_sec + width_px / (zoom * sr)
    const viewWidth = store.zoom > 0 ? 1000 / (store.zoom * 44100) : store.duration;
    const endSec = Math.min(store.offset + viewWidth, store.duration);

    try {
      const res = await fetch(`${API_URL}/waveform?start=${store.offset}&end=${endSec}&n=500`);
      if (res.ok) {
        const data = await res.json();
        setBars(data.bars);
      }
    } catch (e) {}
  };

  useEffect(() => {
    fetchWaveform();
  }, [store.offset, store.zoom, store.duration]);

  useEffect(() => {
    if (!canvasRef.current || !theme) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const h = canvas.height;
    const midY = h / 2;
    const scaleY = midY * 0.9;
    const barW = canvas.width / bars.length;

    bars.forEach((bar, i) => {
      const [mn, mx, intensity] = bar;
      const x = i * barW;
      const y1 = midY + mn * scaleY;
      const y2 = midY + mx * scaleY;

      ctx.strokeStyle = theme.waveform;
      ctx.globalAlpha = Math.max(0.3, intensity);
      ctx.lineWidth = Math.max(1, barW - 1);
      ctx.beginPath();
      ctx.moveTo(x, y1);
      ctx.lineTo(x, y2);
      ctx.stroke();
    });

    // Playhead
    const viewWidth = 1000 / (store.zoom * 44100);
    if (store.position >= store.offset && store.position <= store.offset + viewWidth) {
      const px = ((store.position - store.offset) / viewWidth) * canvas.width;
      ctx.strokeStyle = theme.accent;
      ctx.globalAlpha = 1.0;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(px, 0);
      ctx.lineTo(px, h);
      ctx.stroke();
    }

    ctx.globalAlpha = 1.0;
  }, [bars, theme, store.position, store.offset, store.zoom]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 1.0 / 1.1;
    const rect = canvasRef.current!.getBoundingClientRect();
    const x = e.clientX - rect.left;

    const viewWidth = 1000 / (store.zoom * 44100);
    const mouseSec = store.offset + (x / rect.width) * viewWidth;

    const newZoom = Math.max(store.zoom * factor, 1000 / (store.duration * 44100));
    const newViewWidth = 1000 / (newZoom * 44100);
    const newOffset = Math.max(0, Math.min(mouseSec - (x / rect.width) * newViewWidth, store.duration - newViewWidth));

    store.setViewport(newOffset, newZoom);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    lastX.current = e.clientX;
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging.current) return;
    const dx = e.clientX - lastX.current;
    const viewWidth = 1000 / (store.zoom * 44100);
    const secDelta = (dx / 1000) * viewWidth;

    const newOffset = Math.max(0, Math.min(store.offset - secDelta, store.duration - viewWidth));
    store.setViewport(newOffset, store.zoom);
    lastX.current = e.clientX;
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (isDragging.current && Math.abs(e.clientX - lastX.current) < 5) {
        // Simple click -> seek
        const rect = canvasRef.current!.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const viewWidth = 1000 / (store.zoom * 44100);
        const time = store.offset + (x / rect.width) * viewWidth;
        fetch(`${API_URL}/seek`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time })
        });
        store.setPosition(time);
    }
    isDragging.current = false;
  };

  return (
    <div className="bg-surface rounded-lg h-40 relative overflow-hidden">
      <canvas
        ref={canvasRef}
        width={1000}
        height={160}
        className="w-full h-full cursor-crosshair"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => isDragging.current = false}
      />
    </div>
  );
};
