import React, { useRef, useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

interface TimelineProps {
  offset: number;
  zoom: number;
}

export const Timeline: React.FC<TimelineProps> = ({ offset, zoom }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { loaded, duration, currentTheme, themes, flags, addFlag, moveFlag, setEditingFlagIdx } = useStore();
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current && canvasRef.current) {
        const dpr = window.devicePixelRatio || 1;
        const w = containerRef.current.clientWidth;
        const h = containerRef.current.clientHeight;
        canvasRef.current.width = w * dpr;
        canvasRef.current.height = h * dpr;
        setSize({ width: w, height: h });
      }
    };
    const observer = new ResizeObserver(updateSize);
    if (containerRef.current) observer.observe(containerRef.current);
    updateSize();
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const theme = themes[currentTheme];
    if (!canvas || !theme || size.width === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.width, size.height);

    const span = size.width / zoom;
    const end = offset + span;

    ctx.strokeStyle = theme.grid || '#404040';
    ctx.fillStyle = theme.text || '#e0e0e0';
    ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';

    const step = Math.max(0.1, Math.pow(10, Math.floor(Math.log10(span / 5))));
    const startTick = Math.floor(offset / step) * step;

    for (let t = startTick; t <= end; t += step) {
        const x = (t - offset) * zoom;
        if (x < 0) continue;

        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, size.height);
        ctx.stroke();

        const m = Math.floor(t / 60);
        const s = Math.floor(t % 60);
        const ms = Math.floor((t % 1) * 100);
        if (step < 1) {
            ctx.fillText(`${m}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`, x + 4, 15);
        } else {
            ctx.fillText(`${m}:${s.toString().padStart(2, '0')}`, x + 4, 15);
        }
    }

    flags.forEach((f, idx) => {
        const x = (f.t - offset) * zoom;
        if (x >= 0 && x <= size.width) {
            ctx.strokeStyle = theme.flagRhythm || '#ff4757';
            ctx.lineWidth = dragIdx === idx ? 4 : 2;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, size.height);
            ctx.stroke();

            ctx.fillStyle = theme.surface || '#252525';
            const label = f.name || f.auto_name || '';
            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x - textWidth/2 - 2, 20, textWidth + 4, 12);
            ctx.fillStyle = theme.text || '#fff';
            ctx.fillText(label, x - textWidth/2, 30);
        }
    });
  }, [offset, zoom, themes, currentTheme, duration, flags, dragIdx, size]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!loaded) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const clickT = offset + x / zoom;

    const threshold = 10 / zoom;
    let foundIdx = -1;
    flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundIdx = idx;
        }
    });

    if (e.button === 0) {
        if (foundIdx !== -1) {
            setDragIdx(foundIdx);
            const onMouseMove = (moveEvent: MouseEvent) => {
                const newX = moveEvent.clientX - rect.left;
                const newT = Math.max(0, Math.min(duration, offset + newX / zoom));
                const snappedT = Math.round(newT * 100) / 100;
                moveFlag(foundIdx, snappedT);
            };
            const onMouseUp = () => {
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
                setDragIdx(null);
            };
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        } else {
            const snappedT = Math.round(clickT * 100) / 100;
            addFlag(snappedT);
        }
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const clickT = offset + x / zoom;

    const threshold = 10 / zoom;
    let foundIdx = -1;
    flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundIdx = idx;
        }
    });

    if (foundIdx !== -1) {
        setEditingFlagIdx(foundIdx);
    }
  };

  return (
    <div ref={containerRef} className="h-10 w-full border-b select-none cursor-crosshair"
        style={{ backgroundColor: 'var(--color-surface)', borderBottomColor: 'var(--color-grid)' }}
        onMouseDown={handleMouseDown}
        onContextMenu={handleContextMenu}>
        <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
};
