import React, { useEffect, useRef } from 'react';
import { useStore, API_BASE } from '../store/useStore';
import axios from 'axios';

export const Waveform: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    loaded, position, duration, currentTheme, themes, controlPlayback,
    addHarmonyFlag, setEditingHarmonyFlagIdx,
    offset, zoom, setViewport
  } = useStore();
  const [bars, setBars] = React.useState<number[][]>([]);
  const [size, setSize] = React.useState({ width: 0, height: 0 });
  const [isDragging, setIsDragging] = React.useState(false);
  const inFlightRef = useRef(false);
  const pendingRef = useRef<{ offset: number, zoom: number, width: number } | null>(null);

  const updateSize = React.useCallback(() => {
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

    const fetchBars = async (currentOffset: number, currentZoom: number, currentWidth: number) => {
        if (inFlightRef.current) {
            pendingRef.current = { offset: currentOffset, zoom: currentZoom, width: currentWidth };
            return;
        }

        inFlightRef.current = true;
        try {
            const span = currentWidth / currentZoom;
            const res = await axios.get(`${API_BASE}/audio/waveform`, {
                params: {
                    start: currentOffset,
                    end: currentOffset + span,
                    n_bars: Math.min(currentWidth, 2000)
                }
            });
            setBars(res.data.bars);
        } catch (e) {
            console.error(e);
        } finally {
            inFlightRef.current = false;
            if (pendingRef.current) {
                const next = pendingRef.current;
                pendingRef.current = null;
                fetchBars(next.offset, next.zoom, next.width);
            }
        }
    };

    fetchBars(offset, zoom, size.width || 1000);
  }, [loaded, offset, zoom, duration, size.width]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const theme = themes[currentTheme];
    if (!canvas || !theme || size.width === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.width, size.height);

    const midY = size.height / 2;
    // Use 80% of half-height to ensure a healthy margin and prevent feeling "too tall"
    const scaleY = midY * 0.8;

    const barWidth = size.width / Math.max(bars.length, 1);

    // First pass: Peak envelope (semi-transparent)
    bars.forEach((bar, i) => {
        const [min, max, , , intensity] = bar;
        ctx.globalAlpha = intensity * 0.3;
        ctx.strokeStyle = theme.waveform || theme.accent || '#00aaff';
        ctx.lineWidth = Math.max(1, barWidth);
        ctx.beginPath();
        // Use - for Y because positive samples should go UP (smaller Y)
        const y1 = midY - min * scaleY;
        const y2 = midY - max * scaleY;
        ctx.moveTo(i * barWidth, y1);
        ctx.lineTo(i * barWidth, Math.abs(y2 - y1) < 1 ? y1 - 1 : y2);
        ctx.stroke();
    });

    // Second pass: RMS envelope (more opaque)
    bars.forEach((bar, i) => {
        const [, , mean, rms, intensity] = bar;
        ctx.globalAlpha = intensity;
        ctx.strokeStyle = theme.waveform || theme.accent || '#00aaff';
        ctx.lineWidth = Math.max(1, barWidth);
        ctx.beginPath();
        // RMS is centered around the mean and respects offset
        const y1 = midY - (mean - rms) * scaleY;
        const y2 = midY - (mean + rms) * scaleY;
        ctx.moveTo(i * barWidth, y1);
        ctx.lineTo(i * barWidth, y2);
        ctx.stroke();
    });

    const cursorX = (position - offset) * zoom;
    if (cursorX >= 0 && cursorX <= size.width) {
        ctx.globalAlpha = 1;
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cursorX, 0);
        ctx.lineTo(cursorX, size.height);
        ctx.stroke();
    }
  }, [bars, position, themes, currentTheme, offset, zoom, size]);

  const handleWheel = (e: React.WheelEvent) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const mouseSec = offset + x / zoom;

    const delta = -e.deltaY;
    const factor = delta > 0 ? 1.1 : 1 / 1.1;

    const newZoom = Math.max(zoom * factor, canvasRef.current.width / (duration || 1));
    const newOffset = Math.max(0, Math.min(mouseSec - x / newZoom, duration - canvasRef.current.width / newZoom));

    setViewport(newOffset, newZoom);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) {
        if (e.button === 2 && canvasRef.current) {
            e.preventDefault();
            const rect = canvasRef.current.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const sec = offset + x / zoom;
            const snappedT = Math.round(sec * 100) / 100;
            addHarmonyFlag(snappedT).then((res) => {
                if (res && res.idx !== -1) {
                    setEditingHarmonyFlagIdx(res.idx);
                }
            });
        }
        return;
    }
    const startX = e.clientX;
    const startOffset = offset;
    let dragged = false;
    setIsDragging(true);
    document.body.style.cursor = 'grabbing';

    const onMouseMove = (moveEvent: MouseEvent) => {
        const dx = moveEvent.clientX - startX;
        if (Math.abs(dx) > 5) dragged = true;
        const secDelta = dx / zoom;
        const maxOffset = Math.max(0, duration - (canvasRef.current?.width || 0) / zoom);
        setViewport(Math.max(0, Math.min(startOffset - secDelta, maxOffset)), zoom);
    };

    const onMouseUp = (upEvent: MouseEvent) => {
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        setIsDragging(false);
        document.body.style.cursor = '';
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
        <canvas ref={canvasRef} className="w-full h-full block" style={{ cursor: isDragging ? 'grabbing' : 'grab' }} />
    </div>
  );
};
