import React, { useRef, useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { formatChord, getChordMidiNotes, midiToFreq } from '../store/utils';

interface TimelineProps {
  offset: number;
  zoom: number;
}

export const Timeline: React.FC<TimelineProps> = ({ offset, zoom }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    loaded, duration, currentTheme, themes, flags, harmony_flags,
    addFlag, moveFlag, setEditingFlagIdx,
    addHarmonyFlag, moveHarmonyFlag, setEditingHarmonyFlagIdx,
    loop_mode, loop_range, playTone, stopAllTones
  } = useStore();
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [dragHarmonyIdx, setDragHarmonyIdx] = useState<number | null>(null);
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

    // Draw Loop Range
    if (loaded && loop_mode !== 'none' && loop_range) {
        const [lStart, lEnd] = loop_range;
        const xStart = (lStart - offset) * zoom;
        const xEnd = (lEnd - offset) * zoom;

        if (xEnd > 0 && xStart < size.width) {
            ctx.fillStyle = (theme.accent || '#00aaff') + '22';
            const drawXStart = Math.max(0, xStart);
            const drawXEnd = Math.min(size.width, xEnd);
            ctx.fillRect(drawXStart, 0, drawXEnd - drawXStart, size.height);

            ctx.strokeStyle = (theme.accent || '#00aaff') + '44';
            ctx.lineWidth = 1;
            ctx.beginPath();
            if (xStart >= 0 && xStart <= size.width) {
                ctx.moveTo(xStart, 0);
                ctx.lineTo(xStart, size.height);
            }
            if (xEnd >= 0 && xEnd <= size.width) {
                ctx.moveTo(xEnd, 0);
                ctx.lineTo(xEnd, size.height);
            }
            ctx.stroke();
        }
    }

    const overlapThreshold = 0.01; // 10ms

    // Draw Harmony Flags
    harmony_flags.forEach((f, idx) => {
        const x = (f.t - offset) * zoom;
        if (x >= 0 && x <= size.width) {
            const hasOverlap = flags.some(rf => Math.abs(rf.t - f.t) < overlapThreshold);
            const yStart = 0;
            const yEnd = hasOverlap ? size.height / 2 : size.height;

            ctx.strokeStyle = theme.flagHarmony || '#00aaff';
            ctx.lineWidth = dragHarmonyIdx === idx ? 4 : 2;
            ctx.beginPath();
            ctx.moveTo(x, yStart);
            ctx.lineTo(x, yEnd);
            ctx.stroke();

            ctx.fillStyle = theme.surface || '#252525';
            const label = formatChord(f.chord);

            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x - textWidth/2 - 2, 5, textWidth + 4, 12);
            ctx.fillStyle = theme.text || '#fff';
            ctx.fillText(label, x - textWidth/2, 15);
        }
    });

    // Draw Rhythm Flags
    flags.forEach((f, idx) => {
        const x = (f.t - offset) * zoom;
        if (x >= 0 && x <= size.width) {
            const hasOverlap = harmony_flags.some(hf => Math.abs(hf.t - f.t) < overlapThreshold);
            const yStart = hasOverlap ? size.height / 2 : 0;
            const yEnd = size.height;

            ctx.strokeStyle = theme.flagRhythm || '#ff4757';
            ctx.lineWidth = dragIdx === idx ? 4 : 2;
            ctx.beginPath();
            ctx.moveTo(x, yStart);
            ctx.lineTo(x, yEnd);
            ctx.stroke();

            ctx.fillStyle = theme.surface || '#252525';
            const label = f.name || f.auto_name || '';
            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x - textWidth/2 - 2, 20, textWidth + 4, 12);
            ctx.fillStyle = theme.text || '#fff';
            ctx.fillText(label, x - textWidth/2, 30);
        }

        // Draw subdivisions
        if (f.type === 'rhythm' && idx < flags.length - 1) {
            const nxt = flags[idx + 1];
            let subdiv = f.subdivision || 0;
            if (subdiv === 0) {
                for (let i = idx; i >= 0; i--) {
                    if (flags[i].type === 'rhythm' && flags[i].subdivision !== 0) {
                        subdiv = flags[i].subdivision;
                        break;
                    }
                }
                if (subdiv === 0) subdiv = 1;
            }

            if (subdiv > 1) {
                const span = nxt.t - f.t;
                const step = span / subdiv;
                for (let k = 1; k < subdiv; k++) {
                    const t = f.t + k * step;
                    const sx = (t - offset) * zoom;
                    if (sx >= 0 && sx <= canvas.width) {
                        const baseColor = theme.flagRhythm || '#ff4757';
                        let opacity = "44"; // dimmed
                        if (f.shaded_subdivisions && k % 2 === 1) {
                            opacity = "99"; // brighter
                        }
                        ctx.strokeStyle = baseColor + opacity;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(sx, canvas.height / 2);
                        ctx.lineTo(sx, canvas.height);
                        ctx.stroke();
                    }
                }
            }
        }
    });
  }, [offset, zoom, themes, currentTheme, duration, flags, harmony_flags, dragIdx, dragHarmonyIdx, size, loop_mode, loop_range]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!loaded) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const clickT = offset + x / zoom;

    const threshold = 10 / zoom;
    let foundIdx = -1;
    flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundIdx = idx;
        }
    });

    let foundHarmonyIdx = -1;
    harmony_flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundHarmonyIdx = idx;
        }
    });

    // Handle Overlap Interaction
    if (foundIdx !== -1 && foundHarmonyIdx !== -1) {
        if (y < rect.height / 2) foundIdx = -1;
        else foundHarmonyIdx = -1;
    }

    if (e.button === 0) {
        if (foundHarmonyIdx !== -1) {
            // Play Chord on Hold
            const chord = harmony_flags[foundHarmonyIdx].chord;
            const midis = getChordMidiNotes(chord);
            midis.forEach(m => {
                playTone(midiToFreq(m), 'start');
            });

            setDragHarmonyIdx(foundHarmonyIdx);
            const onMouseMove = (moveEvent: MouseEvent) => {
                const newX = moveEvent.clientX - rect.left;
                const newT = Math.max(0, Math.min(duration, offset + newX / zoom));
                const snappedT = Math.round(newT * 100) / 100;
                moveHarmonyFlag(foundHarmonyIdx, snappedT);
            };
            const onMouseUp = () => {
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
                setDragHarmonyIdx(null);
                stopAllTones();
            };
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        } else if (foundIdx !== -1) {
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
    const y = e.clientY - rect.top;
    const clickT = offset + x / zoom;

    const threshold = 10 / zoom;
    let foundIdx = -1;
    flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundIdx = idx;
        }
    });

    let foundHarmonyIdx = -1;
    harmony_flags.forEach((f, idx) => {
        if (Math.abs(f.t - clickT) < threshold) {
            foundHarmonyIdx = idx;
        }
    });

    // Handle Overlap Interaction
    if (foundIdx !== -1 && foundHarmonyIdx !== -1) {
        if (y < rect.height / 2) foundIdx = -1;
        else foundHarmonyIdx = -1;
    }

    if (foundHarmonyIdx !== -1) {
        setEditingHarmonyFlagIdx(foundHarmonyIdx);
    } else if (foundIdx !== -1) {
        setEditingFlagIdx(foundIdx);
    } else {
        const snappedT = Math.round(clickT * 100) / 100;
        addHarmonyFlag(snappedT).then((newFlag) => {
            if (newFlag) {
                // Wait a tiny bit for the store to settle if needed,
                // though addHarmonyFlag awaits fetchStatus.
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
