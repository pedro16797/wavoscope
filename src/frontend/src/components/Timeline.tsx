import React, { useRef, useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { formatChord, getChordMidiNotes, midiToFreq, getTimelineStep, formatTimelineLabel } from '../store/utils';
import { Tooltip } from './Tooltip';
import { useTranslation } from 'react-i18next';

export const Timeline: React.FC = () => {
    const { t } = useTranslation();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const {
    loaded, duration, currentTheme, themes, flags, harmony_flags, ui_scale,
    addFlag, moveFlag, setEditingFlagIdx,
    addHarmonyFlag, moveHarmonyFlag, setEditingHarmonyFlagIdx,
    loop_mode, loop_range, playTone, stopAllTones,
    offset, zoom, setViewport,
    isRemote
  } = useStore();
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [dragHarmonyIdx, setDragHarmonyIdx] = useState<number | null>(null);
  const [dragT, setDragT] = useState<number | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [hoverCursor, setHoverCursor] = useState<string>('crosshair');

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
    ctx.lineWidth = 1 * ui_scale;
    ctx.fillStyle = theme.text || '#e0e0e0';
    ctx.font = `${10 * ui_scale}px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`;

    const step = getTimelineStep(span);
    const startTick = Math.floor(offset / step) * step;

    for (let t = startTick; t <= end; t += step) {
        const x = (t - offset) * zoom;
        if (x < 0) continue;

        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, size.height);
        ctx.stroke();

        const label = formatTimelineLabel(t, step);
        ctx.fillText(label, x + 4 * ui_scale, 15 * ui_scale);
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
        const t = (dragHarmonyIdx === idx && dragT !== null) ? dragT : f.t;
        const x = (t - offset) * zoom;
        if (x >= 0 && x <= size.width) {
            const hasOverlap = flags.some(rf => Math.abs(rf.t - t) < overlapThreshold);
            const yStart = 0;
            const yEnd = hasOverlap ? size.height / 2 : size.height;

            ctx.strokeStyle = theme.flagHarmony || '#00aaff';
            ctx.lineWidth = (dragHarmonyIdx === idx ? 4 : 2) * ui_scale;
            ctx.beginPath();
            ctx.moveTo(x, yStart);
            ctx.lineTo(x, yEnd);
            ctx.stroke();

            ctx.fillStyle = theme.surface || '#252525';
            const label = formatChord(f.c);

            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x - textWidth/2 - 2 * ui_scale, 5 * ui_scale, textWidth + 4 * ui_scale, 12 * ui_scale);
            ctx.fillStyle = theme.text || '#fff';
            ctx.fillText(label, x - textWidth/2, 15 * ui_scale);
        }
    });

    // Draw Rhythm Flags
    flags.forEach((f, idx) => {
        const t = (dragIdx === idx && dragT !== null) ? dragT : f.t;
        const x = (t - offset) * zoom;
        if (x >= 0 && x <= size.width) {
            const hasOverlap = harmony_flags.some(hf => Math.abs(hf.t - t) < overlapThreshold);
            const yStart = hasOverlap ? size.height / 2 : 0;
            const yEnd = size.height;

            ctx.strokeStyle = theme.flagRhythm || '#ff4757';
            ctx.lineWidth = (dragIdx === idx ? 4 : 2) * ui_scale;
            ctx.beginPath();
            ctx.moveTo(x, yStart);
            ctx.lineTo(x, yEnd);
            ctx.stroke();

            ctx.fillStyle = theme.surface || '#252525';
            const label = f.n || f.auto_name || '';
            const textWidth = ctx.measureText(label).width;
            ctx.fillRect(x - textWidth/2 - 2 * ui_scale, 20 * ui_scale, textWidth + 4 * ui_scale, 12 * ui_scale);
            ctx.fillStyle = theme.text || '#fff';
            ctx.fillText(label, x - textWidth/2, 30 * ui_scale);
        }

        // Draw subdivisions
        if (f.type === 'rhythm' && idx < flags.length - 1) {
            const nxt = flags[idx + 1];
            let subdiv = f.div || 0;
            if (subdiv === 0) {
                for (let i = idx; i >= 0; i--) {
                    if (flags[i].type === 'rhythm' && flags[i].div !== 0) {
                        subdiv = flags[i].div;
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
                        if (f.divshade && k % 2 === 1) {
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
  }, [offset, zoom, themes, currentTheme, duration, flags, harmony_flags, dragIdx, dragHarmonyIdx, dragT, size, loop_mode, loop_range]);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!canvasRef.current || !loaded) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const clickT = offset + x / zoom;
    const threshold = 10 / zoom;

    const isOverFlag = flags.some(f => Math.abs(f.t - clickT) < threshold);
    const isOverHarmony = harmony_flags.some(f => Math.abs(f.t - clickT) < threshold);

    const newCursor = (isOverFlag || isOverHarmony) ? 'pointer' : 'crosshair';
    if (newCursor !== hoverCursor) {
      setHoverCursor(newCursor);
    }
  };

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
            if (isRemote) return;
            // Play Chord on Hold
            const chord = harmony_flags[foundHarmonyIdx].c;
            const midis = getChordMidiNotes(chord);
            playTone(midis.map(m => midiToFreq(m)), 'start', true);

            setDragHarmonyIdx(foundHarmonyIdx);
            document.body.style.cursor = 'ew-resize';
            let latestT = harmony_flags[foundHarmonyIdx].t;
            const onMouseMove = (moveEvent: MouseEvent) => {
                const newX = moveEvent.clientX - rect.left;
                const newT = Math.max(0, Math.min(duration, offset + newX / zoom));
                const snappedT = Math.round(newT * 100) / 100;
                latestT = snappedT;
                setDragT(snappedT);
            };
            const onMouseUp = () => {
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
                document.body.style.cursor = '';
                moveHarmonyFlag(foundHarmonyIdx, latestT).finally(() => {
                    setDragHarmonyIdx(null);
                    setDragT(null);
                });
                stopAllTones();
            };
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        } else if (foundIdx !== -1) {
            if (isRemote) return;
            if (e.shiftKey) {
                if (foundIdx > 0) {
                    const delta = flags[foundIdx].t - flags[foundIdx - 1].t;
                    const newT = flags[foundIdx].t + delta;
                    if (newT <= duration) {
                        addFlag(Math.round(newT * 100) / 100);
                    }
                }
                return;
            }
            setDragIdx(foundIdx);
            document.body.style.cursor = 'ew-resize';
            let latestT = flags[foundIdx].t;
            const onMouseMove = (moveEvent: MouseEvent) => {
                const newX = moveEvent.clientX - rect.left;
                const newT = Math.max(0, Math.min(duration, offset + newX / zoom));
                const snappedT = Math.round(newT * 100) / 100;
                latestT = snappedT;
                setDragT(snappedT);
            };
            const onMouseUp = () => {
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
                document.body.style.cursor = '';
                moveFlag(foundIdx, latestT).finally(() => {
                    setDragIdx(null);
                    setDragT(null);
                });
            };
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        } else {
            if (isRemote) return;
            const snappedT = Math.round(clickT * 100) / 100;
            addFlag(snappedT);
        }
    }
  };

  const handleWheel = (e: React.WheelEvent) => {
    const delta = e.deltaY;
    const scrollAmount = delta / zoom;
    const maxOffset = Math.max(0, duration - size.width / zoom);
    setViewport(Math.max(0, Math.min(offset + scrollAmount, maxOffset)), zoom);
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isRemote) return;
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
        addHarmonyFlag(snappedT).then((res) => {
            if (res && res.idx !== -1) {
                setEditingHarmonyFlagIdx(res.idx);
            }
        });
    }
  };

  const activeCursor = (!isRemote && (dragIdx !== null || dragHarmonyIdx !== null)) ? 'ew-resize' : hoverCursor;

  const lastTouchX = useRef<number | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      lastTouchX.current = e.touches[0].clientX;
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!canvasRef.current || lastTouchX.current === null) return;
    const dx = e.touches[0].clientX - lastTouchX.current;
    const scrollAmount = dx / zoom;
    const maxOffset = Math.max(0, duration - size.width / zoom);
    setViewport(Math.max(0, Math.min(offset - scrollAmount, maxOffset)), zoom);
    lastTouchX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = () => {
    lastTouchX.current = null;
  };

  return (
    <div ref={containerRef} className="w-full border-b select-none cursor-crosshair relative"
        style={{ height: 40 * ui_scale, backgroundColor: 'var(--color-surface)', borderBottomColor: 'var(--color-grid)' }}
        onMouseDown={handleMouseDown}
        onContextMenu={handleContextMenu}
        onWheel={handleWheel}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}>
        <canvas ref={canvasRef} className="w-full h-full block" style={{ cursor: activeCursor }} onMouseMove={handleMouseMove} />

        {/* Chord Flag Tooltips */}
        {harmony_flags.map((f, idx) => {
            const x = (f.t - offset) * zoom;
            if (x < 0 || x > size.width) return null;
            return (
                <div key={`chord-tip-${idx}`} className="absolute top-0 bottom-1/2 w-4 -translate-x-1/2 pointer-events-auto"
                     style={{ left: x }}>
                    <Tooltip content={formatChord(f.c)} shortcut={t('keys.left_click_play')} className="w-full h-full">
                        <div className="w-full h-full" />
                    </Tooltip>
                </div>
            );
        })}

        {/* Rhythm Flag Tooltips */}
        {flags.map((f, idx) => {
            const x = (f.t - offset) * zoom;
            if (x < 0 || x > size.width) return null;

            let subdiv = f.div || 0;
            let isInherited = false;
            if (subdiv === 0) {
                isInherited = true;
                for (let i = idx; i >= 0; i--) {
                    if (flags[i].type === 'rhythm' && flags[i].div !== 0) {
                        subdiv = flags[i].div;
                        break;
                    }
                }
                if (subdiv === 0) subdiv = 1;
            }

            const name = f.n || f.auto_name || '';
            const tipContent = `${name} #${idx + 1} (Subdiv: ${subdiv}${isInherited ? '*' : ''})`;

            return (
                <div key={`rhythm-tip-${idx}`} className="absolute top-1/2 bottom-0 w-4 -translate-x-1/2 pointer-events-auto"
                     style={{ left: x }}>
                    <Tooltip content={tipContent} className="w-full h-full">
                        <div className="w-full h-full" />
                    </Tooltip>
                </div>
            );
        })}
    </div>
  );
};
