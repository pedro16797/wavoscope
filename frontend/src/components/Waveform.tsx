import React, { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import axios from 'axios';

interface WaveformProps {
  offset: number;
  zoom: number;
  onViewportChange: (offset: number, zoom: number) => void;
}

export const Waveform: React.FC<WaveformProps> = ({ offset, zoom, onViewportChange }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { loaded, position, duration, currentTheme, themes, controlPlayback } = useStore();
  const [bars, setBars] = React.useState<any[]>([]);

  const theme = themes[currentTheme] || {};

  const updateSize = React.useCallback(() => {
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
    const fetchBars = async () => {
        try {
            const width = canvasRef.current?.width || 1000;
            const span = width / zoom;
            const res = await axios.get(`http://127.0.0.1:8000/audio/waveform`, {
                params: {
                    start: offset,
                    end: offset + span,
                    n_bars: Math.min(width, 2000)
                }
            });
            setBars(res.data.bars);
        } catch (e) {
            console.error(e);
        }
    };
    fetchBars();
  }, [loaded, offset, zoom, duration]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !theme.waveform) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const midY = canvas.height / 2;
    const scaleY = midY * 0.9;

    const barWidth = canvas.width / Math.max(bars.length, 1);
    bars.forEach((bar, i) => {
        const [min, max, intensity] = bar;
        ctx.globalAlpha = intensity;
        ctx.strokeStyle = theme.waveform;
        ctx.lineWidth = Math.max(1, barWidth);
        ctx.beginPath();
        ctx.moveTo(i * barWidth, midY + min * scaleY);
        ctx.lineTo(i * barWidth, midY + max * scaleY);
        ctx.stroke();
    });

    const cursorX = (position - offset) * zoom;
    if (cursorX >= 0 && cursorX <= canvas.width) {
        ctx.globalAlpha = 1;
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cursorX, 0);
        ctx.lineTo(cursorX, canvas.height);
        ctx.stroke();
    }
  }, [bars, position, theme, offset, zoom]);

  const handleWheel = (e: React.WheelEvent) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const mouseSec = offset + x / zoom;

    const delta = -e.deltaY;
    const factor = delta > 0 ? 1.1 : 1 / 1.1;

    const newZoom = Math.max(zoom * factor, canvasRef.current.width / (duration || 1));
    const newOffset = Math.max(0, Math.min(mouseSec - x / newZoom, duration - canvasRef.current.width / newZoom));

    onViewportChange(newOffset, newZoom);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    const startX = e.clientX;
    const startOffset = offset;
    let dragged = false;

    const onMouseMove = (moveEvent: MouseEvent) => {
        const dx = moveEvent.clientX - startX;
        if (Math.abs(dx) > 5) dragged = true;
        const secDelta = dx / zoom;
        const maxOffset = Math.max(0, duration - (canvasRef.current?.width || 0) / zoom);
        onViewportChange(Math.max(0, Math.min(startOffset - secDelta, maxOffset)), zoom);
    };

    const onMouseUp = (upEvent: MouseEvent) => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        if (!dragged && canvasRef.current) {
            const rect = canvasRef.current.getBoundingClientRect();
            const x = upEvent.clientX - rect.left;
            const sec = offset + x / zoom;
            controlPlayback('seek', sec);
        }
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden"
         onWheel={handleWheel}
         onMouseDown={handleMouseDown}>
        <canvas ref={canvasRef} className="w-full h-full block" />
    </div>
  );
};
