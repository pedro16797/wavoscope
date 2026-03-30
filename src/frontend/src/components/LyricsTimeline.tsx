import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';

/**
 * LyricsTimeline: Interactive track for lyrics transcription.
 *
 * Workflow:
 * 1. Click on empty space or press 'L' to add a lyric at playhead.
 * 2. Type text.
 * 3. Press 'Space' or '-' to commit the word and automatically create
 *    the next lyric element at the current playhead or end of previous.
 * 4. Press 'Enter' to finish editing.
 *
 * Interactions:
 * - Drag center 80% to move.
 * - Drag edges (10%) to resize.
 * - Shift + Left/Right to seek between words.
 * - Arrow keys to move/resize selected lyric by 0.1s.
 */
export const LyricsTimeline: React.FC = () => {
    const { t } = useTranslation();
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const {
        loaded,
        lyrics,
        position,
        controlPlayback,
        addLyric,
        updateLyric,
        removeLyric,
        moveLyric,
        currentTheme,
        themes,
        selectedLyricIdx: selectedIdx,
        setSelectedLyricIdx: setSelectedIdx,
        offset,
        zoom,
        ui_scale,
        setViewport,
        duration: projectDuration,
        isRemote
    } = useStore();

    const [editingIdx, setEditingIdx] = useState<number | null>(null);
    const [editValue, setEditValue] = useState('');
    const [draggingLyric, setDraggingLyric] = useState<{idx: number, t: number, l: number, mode: 'move' | 'left' | 'right'} | null>(null);
    const [viewWidth, setViewWidth] = useState(0);
    const [hoverCursor, setHoverCursor] = useState<string>('crosshair');
    const inputRef = useRef<HTMLInputElement>(null);

    const height = 32 * ui_scale;

    // Stable references for the keyboard listener to avoid frequent re-attachment
    const stateRef = useRef({ lyrics, position, selectedIdx, editingIdx, editValue, loaded });
    useEffect(() => {
        stateRef.current = { lyrics, position, selectedIdx, editingIdx, editValue, loaded };
    }, [lyrics, position, selectedIdx, editingIdx, editValue, loaded]);

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const theme = themes[currentTheme];
        if (!canvas || !theme) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const width = canvas.width / dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, width, height);

        // Draw background
        ctx.fillStyle = theme.surface || '#1a1a1a';
        ctx.fillRect(0, 0, width, height);
        ctx.strokeStyle = theme.grid || '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, height - 0.5);
        ctx.lineTo(width, height - 0.5);
        ctx.stroke();

        // Pass 1: Draw connecting lines for syllables
        lyrics.forEach((lyric, index) => {
            if (lyric.s.endsWith('-') && index < lyrics.length - 1) {
                const nextLyric = lyrics[index + 1];

                let t1 = lyric.t;
                let d1 = lyric.l;
                if (draggingLyric && draggingLyric.idx === index) {
                    t1 = draggingLyric.t;
                    d1 = draggingLyric.l;
                }

                let t2 = nextLyric.t;
                if (draggingLyric && draggingLyric.idx === index + 1) {
                    t2 = draggingLyric.t;
                }

                const x1 = (t1 + d1 - offset) * zoom;
                const x2 = (t2 - offset) * zoom;

                if (x2 >= x1) {
                    ctx.strokeStyle = theme.accent || '#4fd1c5';
                    ctx.lineWidth = 2 * ui_scale;
                    ctx.beginPath();
                    // Extend line slightly into the boxes to ensure visibility for contiguous syllables
                    ctx.moveTo(x1 - 2, height / 2);
                    ctx.lineTo(x2 + 2, height / 2);
                    ctx.stroke();
                }
            }
        });

        // Pass 2: Draw lyric boxes
        lyrics.forEach((lyric, index) => {
            let t = lyric.t;
            let l = lyric.l;

            // Apply local dragging state if active
            if (draggingLyric && draggingLyric.idx === index) {
                t = draggingLyric.t;
                l = draggingLyric.l;
            }

            const x = (t - offset) * zoom;
            const w = l * zoom;

            if (x + w < 0 || x > width) return;

            // Box
            const isSelected = index === selectedIdx;
            const isEditing = index === editingIdx;

            ctx.fillStyle = isEditing ? (theme.accent || '#4fd1c5') + 'AA' :
                          isSelected ? (theme.accent || '#4fd1c5') + '66' :
                          (theme.accent || '#4fd1c5') + '22';

            ctx.strokeStyle = isEditing ? '#ffffff' : (theme.accent || '#4fd1c5');
            ctx.lineWidth = isEditing ? 3 : isSelected ? 2 : 1.5;

            // Rounded rect
            const r = 4 * ui_scale;
            const paddingY = 6 * ui_scale;
            ctx.beginPath();
            ctx.moveTo(x + r, paddingY);
            ctx.lineTo(x + w - r, paddingY);
            ctx.quadraticCurveTo(x + w, paddingY, x + w, paddingY + r);
            ctx.lineTo(x + w, height - paddingY - r);
            ctx.quadraticCurveTo(x + w, height - paddingY, x + w - r, height - paddingY);
            ctx.lineTo(x + r, height - paddingY);
            ctx.quadraticCurveTo(x, height - paddingY, x, height - paddingY - r);
            ctx.lineTo(x, paddingY + r);
            ctx.quadraticCurveTo(x, paddingY, x + r, paddingY);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Text
            ctx.save();
            ctx.beginPath();
            ctx.rect(x, 0, w, height);
            ctx.clip();

            ctx.font = `${12 * ui_scale}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            let text = (isEditing && index === editingIdx) ? editValue : lyric.s;
            if (text.endsWith('-') && !isEditing) {
                text = text.slice(0, -1);
            }
            const metrics = ctx.measureText(text);

            if (w > 12) {
                // Fade opacity as box gets very small
                if (w < 48) {
                    ctx.globalAlpha = Math.max(0, (w - 12) / 36);
                }

                if (metrics.width > w - 8) {
                    // Use gradient to fade text edges if it doesn't fit
                    const gradient = ctx.createLinearGradient(x, 0, x + w, 0);
                    const color = theme.text || 'white';
                    gradient.addColorStop(0, 'transparent');
                    gradient.addColorStop(0.15, color);
                    gradient.addColorStop(0.85, color);
                    gradient.addColorStop(1, 'transparent');
                    ctx.fillStyle = gradient;
                } else {
                    ctx.fillStyle = theme.text || 'white';
                }
                ctx.fillText(text, x + w / 2, height / 2);
            }
            ctx.restore();
        });

        const playheadX = (position - offset) * zoom;
        if (playheadX >= 0 && playheadX <= width) {
            ctx.strokeStyle = theme.playhead || '#f56565';
            ctx.lineWidth = 2 * ui_scale;
            ctx.beginPath();
            ctx.moveTo(playheadX, 0);
            ctx.lineTo(playheadX, height);
            ctx.stroke();
        }
    }, [lyrics, position, zoom, offset, editingIdx, selectedIdx, themes, currentTheme, draggingLyric, editValue]);

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current && canvasRef.current) {
                const dpr = window.devicePixelRatio || 1;
                const width = containerRef.current.clientWidth;
                canvasRef.current.width = width * dpr;
                canvasRef.current.height = height * dpr;
                setViewWidth(width);
                draw();
            }
        };
        const observer = new ResizeObserver(updateSize);
        if (containerRef.current) observer.observe(containerRef.current);
        updateSize();
        return () => observer.disconnect();
    }, [draw]);

    useEffect(() => {
        draw();
    }, [draw]);

    const addLyricAt = useCallback(async (t: number, s: string = '', l: number = 1.0) => {
        const { lyrics: currentLyrics } = stateRef.current;
        const snappedT = Math.round(t * 100) / 100;

        // Clamping duration so it doesn't overlap with the next lyric
        const nextLyric = currentLyrics.find(lyr => lyr.t > snappedT);
        let finalDuration = l;
        if (nextLyric) {
            finalDuration = Math.min(l, nextLyric.t - snappedT);
            if (finalDuration < 0.2) finalDuration = 0.2;
        }

        const res = await addLyric({ s, t: snappedT, l: finalDuration });
        if (res) {
            setSelectedIdx(res.idx);
            setEditingIdx(res.idx);
            setEditValue(s);
        }
        return res;
    }, [addLyric, setSelectedIdx]);

    const finishEditing = useCallback(async () => {
        const { editingIdx: currentEditingIdx, editValue: currentEditValue } = stateRef.current;
        if (currentEditingIdx !== null) {
            const trimmed = currentEditValue.trim();
            if (trimmed === '') {
                await removeLyric(currentEditingIdx);
                setSelectedIdx(null);
            } else {
                const res = await updateLyric(currentEditingIdx, { s: trimmed });
                if (res) setSelectedIdx(res.idx);
            }
            setEditingIdx(null);
            setEditValue('');
        }
    }, [removeLyric, updateLyric, setSelectedIdx]);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!canvasRef.current || !loaded) return;
        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(lyr => time >= lyr.t && time <= lyr.t + lyr.l);
        if (clickedIdx !== -1) {
            const lyric = lyrics[clickedIdx];
            const relativePos = (time - lyric.t) / lyric.l;
            const newCursor = (relativePos < 0.1 || relativePos > 0.9) ? 'ew-resize' : 'pointer';
            if (newCursor !== hoverCursor) {
                setHoverCursor(newCursor);
            }
        } else {
            if (hoverCursor !== 'crosshair') {
                setHoverCursor('crosshair');
            }
        }
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        if (!loaded) return;
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(lyr => time >= lyr.t && time <= lyr.t + lyr.l);

        if (e.button === 0) { // Left click
            if (clickedIdx !== -1) {
                if (isRemote) return;
                const isAlreadySelected = selectedIdx === clickedIdx;
                const lyric = lyrics[clickedIdx];
                const relativePos = (time - lyric.t) / lyric.l;
                let dragMode: 'move' | 'left' | 'right' = 'move';

                // 10% edge detection for resizing
                if (relativePos < 0.1) dragMode = 'left';
                else if (relativePos > 0.9) dragMode = 'right';

                if (!isAlreadySelected) {
                    setSelectedIdx(clickedIdx);
                }

                if (editingIdx !== null && editingIdx !== clickedIdx) {
                    finishEditing();
                }

                if (dragMode === 'move') {
                    document.body.style.cursor = 'grabbing';
                } else {
                    document.body.style.cursor = 'ew-resize';
                }

                const startX = e.clientX;
                const startT = lyric.t;
                const startL = lyric.l;
                let hasMoved = false;

                const onMouseMove = (moveEvent: MouseEvent) => {
                    const dx = moveEvent.clientX - startX;
                    if (Math.abs(dx) > 5) hasMoved = true;
                    const dt = dx / zoom;

                    let newT = startT;
                    let newL = startL;

                    if (dragMode === 'move') {
                        newT = Math.round((startT + dt) * 100) / 100;
                        const prev = lyrics[clickedIdx - 1];
                        const next = lyrics[clickedIdx + 1];
                        if (prev && newT < prev.t + prev.l) newT = prev.t + prev.l;
                        if (next && newT + lyric.l > next.t) newT = next.t - lyric.l;
                        if (newT < 0) newT = 0;
                    } else if (dragMode === 'left') {
                        newT = Math.round((startT + dt) * 100) / 100;
                        const prev = lyrics[clickedIdx - 1];
                        const minT = prev ? prev.t + prev.l : 0;
                        if (newT < minT) newT = minT;

                        newL = startL - (newT - startT);
                        if (newL < 0.2) {
                            newL = 0.2;
                            newT = startT + startL - 0.2;
                        }
                    } else if (dragMode === 'right') {
                        newL = Math.round((startL + dt) * 100) / 100;
                        if (newL < 0.2) newL = 0.2;
                        const next = lyrics[clickedIdx + 1];
                        if (next && lyric.t + newL > next.t) newL = next.t - lyric.t;
                    }

                    setDraggingLyric({ idx: clickedIdx, t: newT, l: newL, mode: dragMode });
                };

                const onMouseUp = () => {
                    window.removeEventListener('mousemove', onMouseMove);
                    window.removeEventListener('mouseup', onMouseUp);
                    document.body.style.cursor = '';

                    if (!hasMoved && isAlreadySelected) {
                        setSelectedIdx(null);
                    }

                    setDraggingLyric(currentDragging => {
                        if (currentDragging) {
                            const { idx, t, l, mode } = currentDragging;
                            const promise = mode === 'move'
                                ? moveLyric(idx, t)
                                : updateLyric(idx, { t, l });

                            promise.then(res => {
                                if (res) setSelectedIdx(res.idx);
                            }).finally(() => {
                                setDraggingLyric(null);
                            });
                            return currentDragging; // Keep visual state until backend confirms
                        }
                        return null;
                    });
                };

                window.addEventListener('mousemove', onMouseMove);
                window.addEventListener('mouseup', onMouseUp);
            } else {
                if (isRemote) return;
                if (editingIdx !== null) {
                    finishEditing();
                }
                const snappedT = Math.round(time * 100) / 100;
                addLyricAt(snappedT);
            }
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        if (!loaded || e.button !== 0 || isRemote) return;
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(lyr => time >= lyr.t && time <= lyr.t + lyr.l);
        if (clickedIdx !== -1) {
            setSelectedIdx(clickedIdx);
            setEditingIdx(clickedIdx);
            setEditValue(lyrics[clickedIdx].s);
        }
    };

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            const { loaded, lyrics, position, selectedIdx, editingIdx, editValue } = stateRef.current;
            if (!loaded || isRemote) return;

            // Global transcription key: 'V'
            if (e.key.toLowerCase() === 'v' && !e.shiftKey) {
                if ((e.target as HTMLElement).tagName !== 'INPUT') {
                    e.preventDefault();
                    e.stopImmediatePropagation();

                    if (selectedIdx !== null && selectedIdx < lyrics.length) {
                        const current = lyrics[selectedIdx];
                        if (editingIdx !== null) {
                            // Already editing, commit and move to next
                            const trimmed = editValue.trim();
                            if (trimmed === '') {
                                removeLyric(editingIdx);
                                setEditingIdx(null);
                                addLyricAt(position);
                            } else {
                                setEditingIdx(null);
                                updateLyric(editingIdx, { s: trimmed }).then(() => {
                                    const nextStart = Math.max(position, current.t + current.l);
                                    addLyricAt(nextStart);
                                });
                            }
                        } else {
                            const nextStart = Math.max(position, current.t + current.l);
                            addLyricAt(nextStart);
                        }
                    } else {
                        addLyricAt(position);
                    }
                }
                return;
            }

            // Shortcuts when something is selected
            if (selectedIdx !== null) {
                const navKeys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'a', 'A', 'd', 'D', 'w', 'W', 's', 'S'];
                if (navKeys.includes(e.key)) {
                    if ((e.target as HTMLElement).tagName !== 'INPUT') {
                        if ((e.key.toLowerCase() === 's') && (e.ctrlKey || e.metaKey)) {
                            // Let global handler catch Ctrl+S
                        } else {
                            e.preventDefault();
                            e.stopImmediatePropagation();
                        }
                    }
                }

                if (e.key === 'Enter') {
                    if (editingIdx === null) {
                        setEditingIdx(selectedIdx);
                        setEditValue(lyrics[selectedIdx].s);
                    } else {
                        finishEditing();
                    }
                } else if (e.key === 'Escape') {
                    finishEditing();
                    setSelectedIdx(null);
                } else if (e.shiftKey && (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a')) {
                    e.preventDefault();
                    const lyric = lyrics[selectedIdx];
                    if (position > lyric.t + lyric.l * 0.1) {
                        controlPlayback('seek', lyric.t);
                    } else if (selectedIdx > 0) {
                        const prev = lyrics[selectedIdx - 1];
                        controlPlayback('seek', prev.t);
                        setSelectedIdx(selectedIdx - 1);
                    }
                } else if (e.shiftKey && (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd')) {
                    e.preventDefault();
                    if (selectedIdx < lyrics.length - 1) {
                        const next = lyrics[selectedIdx + 1];
                        controlPlayback('seek', next.t);
                        setSelectedIdx(selectedIdx + 1);
                    }
                } else if ((e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') && !e.shiftKey) {
                    if (editingIdx !== null) return;
                    e.preventDefault();
                    let newT = Math.round((lyrics[selectedIdx].t - 0.1) * 100) / 100;
                    const prev = lyrics[selectedIdx - 1];
                    if (prev && newT < prev.t + prev.l) newT = prev.t + prev.l;
                    moveLyric(selectedIdx, Math.max(0, newT)).then(res => { if(res) setSelectedIdx(res.idx); });
                } else if ((e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') && !e.shiftKey) {
                    if (editingIdx !== null) return;
                    e.preventDefault();
                    let newT = Math.round((lyrics[selectedIdx].t + 0.1) * 100) / 100;
                    const next = lyrics[selectedIdx + 1];
                    if (next && newT + lyrics[selectedIdx].l > next.t) newT = next.t - lyrics[selectedIdx].l;
                    moveLyric(selectedIdx, newT).then(res => { if(res) setSelectedIdx(res.idx); });
                } else if (e.key === 'ArrowUp' || e.key.toLowerCase() === 'w') {
                    if (editingIdx !== null) return;
                    e.preventDefault();
                    let newL = Math.round((lyrics[selectedIdx].l + 0.1) * 100) / 100;
                    const next = lyrics[selectedIdx + 1];
                    if (next && lyrics[selectedIdx].t + newL > next.t) newL = next.t - lyrics[selectedIdx].t;
                    updateLyric(selectedIdx, { l: newL }).then(res => { if(res) setSelectedIdx(res.idx); });
                } else if (e.key === 'ArrowDown' || e.key.toLowerCase() === 's') {
                    if (editingIdx !== null) return;
                    if (e.ctrlKey || e.metaKey) return;
                    e.preventDefault();
                    updateLyric(selectedIdx, { l: Math.max(0.2, Math.round((lyrics[selectedIdx].l - 0.1) * 100) / 100) }).then(res => { if(res) setSelectedIdx(res.idx); });
                }
            } else {
                // Seek between words even if none selected
                if (e.shiftKey && (e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a')) {
                    e.preventDefault();
                    const prev = [...lyrics].reverse().find(lyr => lyr.t < position - 0.1);
                    if (prev) {
                        controlPlayback('seek', prev.t);
                        const idx = lyrics.findIndex(lyr => lyr.t === prev.t);
                        setSelectedIdx(idx);
                    }
                } else if (e.shiftKey && (e.key === 'ArrowRight' || e.key.toLowerCase() === 'd')) {
                    e.preventDefault();
                    const next = lyrics.find(lyr => lyr.t > position + 0.1);
                    if (next) {
                        controlPlayback('seek', next.t);
                        const idx = lyrics.findIndex(lyr => lyr.t === next.t);
                        setSelectedIdx(idx);
                    }
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown, { capture: true });
        return () => window.removeEventListener('keydown', handleKeyDown, { capture: true });
    }, [controlPlayback, moveLyric, updateLyric, removeLyric, addLyricAt, setSelectedIdx]);

    useEffect(() => {
        if (editingIdx !== null && inputRef.current) {
            inputRef.current.focus();
        }
    }, [editingIdx]);

    // Auto-scroll logic
    useEffect(() => {
        if (selectedIdx === null || selectedIdx >= lyrics.length || viewWidth === 0) return;
        const lyric = lyrics[selectedIdx];
        const span = viewWidth / zoom;
        const margin = 0.05 * span; // 5% margin

        const start = lyric.t;
        const end = lyric.t + lyric.l;

        let newOffset = offset;

        if (lyric.l > span) {
            // If lyric is wider than view, just ensure start is visible with small margin
            if (start < offset || start > offset + margin) {
                newOffset = Math.max(0, start - margin);
            }
        } else {
            // Ensure whole lyric is visible
            if (start < offset + margin) {
                newOffset = Math.max(0, start - margin);
            } else if (end > offset + span - margin) {
                newOffset = Math.min(projectDuration - span, end - span + margin);
            }
        }

        if (Math.abs(newOffset - offset) > 0.001) {
            setViewport(newOffset, zoom);
        }
    }, [selectedIdx, lyrics, viewWidth, zoom, projectDuration, setViewport]);

    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === ' ' || e.key === '-') {
            e.preventDefault();
            e.stopPropagation();
            const { editingIdx: currentEditingIdx, editValue: currentEditValue, lyrics: currentLyrics } = stateRef.current;
            const trimmed = currentEditValue.trim();
            if (currentEditingIdx !== null) {
                const current = currentLyrics[currentEditingIdx];
                setEditingIdx(null);
                setEditValue('');

                const textToSave = e.key === '-' ? trimmed + '-' : trimmed;

                if (trimmed === '' && e.key !== '-') {
                    removeLyric(currentEditingIdx);
                    addLyricAt(current.t, '', current.l);
                } else {
                    updateLyric(currentEditingIdx, { s: textToSave });
                    addLyricAt(current.t + current.l, '', current.l);
                }
            }
        }
    };

    const activeCursor = (!isRemote && draggingLyric)
        ? (draggingLyric.mode === 'move' ? 'grabbing' : 'ew-resize')
        : hoverCursor;

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
        const maxOffset = Math.max(0, projectDuration - viewWidth / zoom);
        setViewport(Math.max(0, Math.min(offset - scrollAmount, maxOffset)), zoom);
        lastTouchX.current = e.touches[0].clientX;
    };

    const handleTouchEnd = () => {
        lastTouchX.current = null;
    };

    return (
        <div ref={containerRef} className="relative w-full select-none bg-surface border-b overflow-hidden" style={{ height: height, borderBottomColor: 'var(--color-grid)' }}>
            <canvas
                ref={canvasRef}
                onMouseMove={handleMouseMove}
                onMouseDown={handleMouseDown}
                onDoubleClick={handleDoubleClick}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
                onContextMenu={(e) => e.preventDefault()}
                className="w-full h-full block"
                style={{ cursor: activeCursor }}
            />
            {editingIdx !== null && lyrics[editingIdx] && (
                <div
                    className="absolute z-10"
                    style={{
                        left: (lyrics[editingIdx].t - offset) * zoom,
                        top: 4 * ui_scale,
                        width: Math.max(80 * ui_scale, lyrics[editingIdx].l * zoom),
                        height: 24 * ui_scale
                    }}
                >
                    <input
                        ref={inputRef}
                        type="text"
                        placeholder={t('lyrics.placeholder')}
                        className="w-full h-full bg-gray-900 text-white text-xs px-2 border-2 rounded outline-none shadow-2xl"
                        style={{ borderColor: themes[currentTheme]?.accent || '#4fd1c5' }}
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={handleInputKeyDown}
                        onBlur={finishEditing}
                        autoFocus
                    />
                </div>
            )}
        </div>
    );
};
