import React, { useEffect, useRef } from 'react';
import { useStore, API_BASE } from '../store/useStore';
import axios from 'axios';

interface WaveformProps {
  offset: number;
  zoom: number;
  onViewportChange: (offset: number, zoom: number) => void;
}

export const Waveform: React.FC<WaveformProps> = ({ offset, zoom, onViewportChange }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { loaded, position, duration, currentTheme, themes, controlPlayback, addHarmonyFlag, setEditingHarmonyFlagIdx } = useStore();
  const [bars, setBars] = React.useState<number[][]>([]);
  const [size, setSize] = React.useState({ width: 0, height: 0 });
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
        const [min, max, , intensity] = bar;
        ctx.globalAlpha = intensity * 0.3;
        ctx.strokeStyle = theme.waveform || theme.accent || '#00aaff';
        ctx.lineWidth = Math.max(1, barWidth);
        ctx.beginPath();
        ctx.moveTo(i * barWidth, midY + min * scaleY);
        ctx.lineTo(i * barWidth, midY + max * scaleY);
        ctx.stroke();
    });

    // Second pass: RMS envelope (more opaque)
    bars.forEach((bar, i) => {
        const [, , rms, intensity] = bar;
        ctx.globalAlpha = intensity;
        ctx.strokeStyle = theme.waveform || theme.accent || '#00aaff';
        ctx.lineWidth = Math.max(1, barWidth);
        ctx.beginPath();
        ctx.moveTo(i * barWidth, midY - rms * scaleY);
        ctx.lineTo(i * barWidth, midY + rms * scaleY);
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

    onViewportChange(newOffset, newZoom);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) {
        if (e.button === 2 && canvasRef.current) {
            e.preventDefault();
            const rect = canvasRef.current.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const sec = offset + x / zoom;
            const snappedT = Math.round(sec * 100) / 100;
            addHarmonyFlag(snappedT).then((newFlag) => {
                if (newFlag) {
                    // Small delay to ensure store update has propagated to all components if needed
                    setTimeout(() => {
                        const updatedFlags = useStore.getState().harmony_flags;
                        let bestIdx = -1;
                        let minDiff = Infinity;
                        updatedFlags.forEach((f, i) => {
                            const diff = Math.abs(f.t - snappedT);
                            if (diff < minDiff) {
                                minDiff = diff;
                                bestIdx = i;
                            }
                        });
                        if (bestIdx !== -1) {
                            setEditingHarmonyFlagIdx(bestIdx);
                        }
                    }, 100);
                }
            });
        }
        return;
    }
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
