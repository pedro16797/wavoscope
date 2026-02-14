import React, { useEffect, useRef } from 'react';
import { useStore } from './store';

export const Timeline: React.FC = () => {
  const store = useStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    const viewWidth = 1000 / (store.zoom * 44100);
    const end = store.offset + viewWidth;

    ctx.strokeStyle = '#404040';
    ctx.fillStyle = '#a0a0a0';
    ctx.font = '10px monospace';

    // Major ticks every second or based on zoom
    const step = viewWidth > 10 ? 5 : (viewWidth > 2 ? 1 : 0.1);
    const firstTick = Math.ceil(store.offset / step) * step;

    for (let t = firstTick; t <= end; t += step) {
      const x = ((t - store.offset) / viewWidth) * w;
      ctx.beginPath();
      ctx.moveTo(x, h);
      ctx.lineTo(x, h - 10);
      ctx.stroke();
      ctx.fillText(t.toFixed(1) + 's', x + 2, h - 2);
    }
  }, [store.offset, store.zoom, store.duration]);

  return (
    <div className="h-6 bg-surface border-b border-grid">
      <canvas ref={canvasRef} width={1000} height={24} className="w-full h-full" />
    </div>
  );
};
