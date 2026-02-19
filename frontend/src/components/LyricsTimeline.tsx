import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useStore } from '../store/useStore';

interface LyricsTimelineProps {
    offset: number;
    zoom: number;
}

export const LyricsTimeline: React.FC<LyricsTimelineProps> = ({ offset, zoom }) => {
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
        setSelectedLyricIdx: setSelectedIdx
    } = useStore();

    const [editingIdx, setEditingIdx] = useState<number | null>(null);
    const [editValue, setEditValue] = useState('');
    const inputRef = useRef<HTMLInputElement>(null);

    const height = 32;

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
        ctx.beginPath();
        ctx.moveTo(0, height - 0.5);
        ctx.lineTo(width, height - 0.5);
        ctx.stroke();

        lyrics.forEach((lyric, index) => {
            const x = (lyric.timestamp - offset) * zoom;
            const w = lyric.duration * zoom;

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
            const r = 4;
            const paddingY = 6;
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
            ctx.fillStyle = theme.text || 'white';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            let text = lyric.text;
            const metrics = ctx.measureText(text);
            if (metrics.width > w - 10) {
                text = text.substring(0, Math.max(1, Math.floor((w-10)/8))) + '...';
            }

            ctx.fillText(text, x + w / 2, height / 2);
        });

        const playheadX = (position - offset) * zoom;
        if (playheadX >= 0 && playheadX <= width) {
            ctx.strokeStyle = theme.playhead || '#f56565';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(playheadX, 0);
            ctx.lineTo(playheadX, height);
            ctx.stroke();
        }
    }, [lyrics, position, zoom, offset, editingIdx, selectedIdx, themes, currentTheme]);

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current && canvasRef.current) {
                const dpr = window.devicePixelRatio || 1;
                canvasRef.current.width = containerRef.current.clientWidth * dpr;
                canvasRef.current.height = height * dpr;
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

    const handleMouseDown = (e: React.MouseEvent) => {
        if (!loaded) return;
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(l => time >= l.timestamp && time <= l.timestamp + l.duration);

        if (e.button === 2) { // Right click
            return;
        }

        if (e.button === 0) { // Left click
            if (clickedIdx !== -1) {
                const lyric = lyrics[clickedIdx];
                const relativePos = (time - lyric.timestamp) / lyric.duration;
                let dragMode: 'move' | 'left' | 'right' = 'move';
                if (relativePos < 0.1) dragMode = 'left';
                else if (relativePos > 0.9) dragMode = 'right';

                setSelectedIdx(clickedIdx);
                if (editingIdx !== null && editingIdx !== clickedIdx) {
                    finishEditing();
                }
                const startX = e.clientX;
                const startT = lyric.timestamp;
                const startD = lyric.duration;

                const onMouseMove = (moveEvent: MouseEvent) => {
                    const dx = moveEvent.clientX - startX;
                    const dt = dx / zoom;

                    if (dragMode === 'move') {
                        let newT = Math.round((startT + dt) * 100) / 100;
                        const prev = lyrics[clickedIdx - 1];
                        const next = lyrics[clickedIdx + 1];
                        if (prev && newT < prev.timestamp + prev.duration) newT = prev.timestamp + prev.duration;
                        if (next && newT + lyric.duration > next.timestamp) newT = next.timestamp - lyric.duration;
                        if (newT < 0) newT = 0;
                        moveLyric(clickedIdx, newT).then(res => { if (res) setSelectedIdx(res.idx); });
                    } else if (dragMode === 'left') {
                        let newT = Math.round((startT + dt) * 100) / 100;
                        const prev = lyrics[clickedIdx - 1];
                        const minT = prev ? prev.timestamp + prev.duration : 0;
                        if (newT < minT) newT = minT;

                        let newD = startD - (newT - startT);
                        if (newD < 0.2) {
                            newD = 0.2;
                            newT = startT + startD - 0.2;
                        }
                        updateLyric(clickedIdx, { timestamp: newT, duration: newD }).then(res => { if (res) setSelectedIdx(res.idx); });
                    } else if (dragMode === 'right') {
                        let newD = Math.round((startD + dt) * 100) / 100;
                        if (newD < 0.2) newD = 0.2;
                        const next = lyrics[clickedIdx + 1];
                        if (next && lyric.timestamp + newD > next.timestamp) newD = next.timestamp - lyric.timestamp;
                        updateLyric(clickedIdx, { duration: newD }).then(res => { if (res) setSelectedIdx(res.idx); });
                    }
                };

                const onMouseUp = () => {
                    window.removeEventListener('mousemove', onMouseMove);
                    window.removeEventListener('mouseup', onMouseUp);
                };

                window.addEventListener('mousemove', onMouseMove);
                window.addEventListener('mouseup', onMouseUp);
            } else {
                if (editingIdx !== null) {
                    finishEditing();
                }
                const snappedT = Math.round(time * 100) / 100;
                addLyricAt(snappedT);
            }
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        if (!loaded || e.button !== 0) return;
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(l => time >= l.timestamp && time <= l.timestamp + l.duration);
        if (clickedIdx !== -1) {
            setEditingIdx(clickedIdx);
            setEditValue(lyrics[clickedIdx].text);
        }
    };

    const addLyricAt = useCallback((t: number) => {
        const snappedT = Math.round(t * 100) / 100;

        // Clamping duration so it doesn't overlap with the next lyric
        const nextLyric = lyrics.find(l => l.timestamp > snappedT);
        let duration = 1.0;
        if (nextLyric) {
            duration = Math.min(1.0, nextLyric.timestamp - snappedT);
            if (duration < 0.2) duration = 0.2;
        }

        addLyric({
            text: '',
            timestamp: snappedT,
            duration: duration
        }).then((res) => {
            if (res) {
                setSelectedIdx(res.idx);
                setEditingIdx(res.idx);
                setEditValue('');
            }
        });
    }, [addLyric, lyrics]);

    const finishEditing = useCallback(() => {
        if (editingIdx !== null) {
            const trimmed = editValue.trim();
            if (trimmed === '') {
                removeLyric(editingIdx);
                setSelectedIdx(null);
            } else {
                updateLyric(editingIdx, { text: trimmed }).then(res => {
                    if (res) setSelectedIdx(res.idx);
                });
            }
            setEditingIdx(null);
        }
    }, [editingIdx, editValue, updateLyric, removeLyric]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key.toLowerCase() === 'l') {
                if (loaded && (e.target as HTMLElement).tagName !== 'INPUT') {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    const state = useStore.getState();
                    const currentLyrics = state.lyrics;

                    if (selectedIdx !== null && selectedIdx < currentLyrics.length) {
                        const current = currentLyrics[selectedIdx];
                        if (editingIdx !== null) {
                            const trimmed = editValue.trim();
                            if (trimmed === '') {
                                removeLyric(editingIdx);
                                setSelectedIdx(null);
                                addLyricAt(position);
                                return;
                            } else {
                                updateLyric(editingIdx, { text: trimmed }).then(res => {
                                    if (res) setSelectedIdx(res.idx);
                                });
                                setEditingIdx(null);
                            }
                        }
                        const nextStart = Math.max(position, current.timestamp + current.duration);
                        addLyricAt(nextStart);
                    } else {
                        addLyricAt(position);
                    }
                }
                return;
            }

            if (selectedIdx === null) {
                if (e.shiftKey && e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prev = [...lyrics].reverse().find(l => l.timestamp < position - 0.1);
                    if (prev) {
                        controlPlayback('seek', prev.timestamp);
                        const idx = lyrics.findIndex(l => l.timestamp === prev.timestamp);
                        setSelectedIdx(idx);
                    }
                } else if (e.shiftKey && e.key === 'ArrowRight') {
                    e.preventDefault();
                    const next = lyrics.find(l => l.timestamp > position + 0.1);
                    if (next) {
                        controlPlayback('seek', next.timestamp);
                        const idx = lyrics.findIndex(l => l.timestamp === next.timestamp);
                        setSelectedIdx(idx);
                    }
                }
                return;
            }

            // If an element is selected
            if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Enter', 'Escape'].includes(e.key)) {
                e.stopImmediatePropagation();
            }

            if (e.key === 'Enter') {
                if (editingIdx === null) {
                    setEditingIdx(selectedIdx);
                    setEditValue(lyrics[selectedIdx].text);
                } else {
                    finishEditing();
                }
            } else if (e.key === 'Escape') {
                finishEditing();
                setSelectedIdx(null);
            } else if (e.shiftKey && e.key === 'ArrowLeft') {
                e.preventDefault();
                const lyric = lyrics[selectedIdx];
                if (position > lyric.timestamp + lyric.duration * 0.1) {
                    controlPlayback('seek', lyric.timestamp);
                } else if (selectedIdx > 0) {
                    const prev = lyrics[selectedIdx - 1];
                    controlPlayback('seek', prev.timestamp);
                    setSelectedIdx(selectedIdx - 1);
                }
            } else if (e.shiftKey && e.key === 'ArrowRight') {
                e.preventDefault();
                if (selectedIdx < lyrics.length - 1) {
                    const next = lyrics[selectedIdx + 1];
                    controlPlayback('seek', next.timestamp);
                    setSelectedIdx(selectedIdx + 1);
                }
            } else if (e.key === 'ArrowLeft' && !e.shiftKey) {
                e.preventDefault();
                if (editingIdx !== null && (e.target as HTMLElement).tagName === 'INPUT') return;
                let newT = lyrics[selectedIdx].timestamp - 0.1;
                const prev = lyrics[selectedIdx - 1];
                if (prev && newT < prev.timestamp + prev.duration) newT = prev.timestamp + prev.duration;
                moveLyric(selectedIdx, Math.max(0, newT)).then(res => { if(res) setSelectedIdx(res.idx); });
            } else if (e.key === 'ArrowRight' && !e.shiftKey) {
                e.preventDefault();
                if (editingIdx !== null && (e.target as HTMLElement).tagName === 'INPUT') return;
                let newT = lyrics[selectedIdx].timestamp + 0.1;
                const next = lyrics[selectedIdx + 1];
                if (next && newT + lyrics[selectedIdx].duration > next.timestamp) newT = next.timestamp - lyrics[selectedIdx].duration;
                moveLyric(selectedIdx, newT).then(res => { if(res) setSelectedIdx(res.idx); });
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (editingIdx !== null && (e.target as HTMLElement).tagName === 'INPUT') return;
                let newD = lyrics[selectedIdx].duration + 0.1;
                const next = lyrics[selectedIdx + 1];
                if (next && lyrics[selectedIdx].timestamp + newD > next.timestamp) newD = next.timestamp - lyrics[selectedIdx].timestamp;
                updateLyric(selectedIdx, { duration: newD }).then(res => { if(res) setSelectedIdx(res.idx); });
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (editingIdx !== null && (e.target as HTMLElement).tagName === 'INPUT') return;
                updateLyric(selectedIdx, { duration: Math.max(0.2, lyrics[selectedIdx].duration - 0.1) }).then(res => { if(res) setSelectedIdx(res.idx); });
            }
        };

        window.addEventListener('keydown', handleKeyDown, { capture: true });
        return () => window.removeEventListener('keydown', handleKeyDown, { capture: true });
    }, [selectedIdx, editingIdx, lyrics, position, editValue, finishEditing, addLyricAt, controlPlayback, moveLyric, updateLyric, loaded]);

    useEffect(() => {
        if (editingIdx !== null && inputRef.current) {
            inputRef.current.focus();
        }
    }, [editingIdx]);

    return (
        <div ref={containerRef} className="relative w-full h-8 select-none bg-surface border-b" style={{ borderBottomColor: 'var(--color-grid)' }}>
            <canvas
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onDoubleClick={handleDoubleClick}
                onContextMenu={(e) => e.preventDefault()}
                className="cursor-crosshair w-full h-full block"
            />
            {editingIdx !== null && lyrics[editingIdx] && (
                <div
                    className="absolute z-10"
                    style={{
                        left: (lyrics[editingIdx].timestamp - offset) * zoom,
                        top: 4,
                        width: Math.max(80, lyrics[editingIdx].duration * zoom),
                        height: 24
                    }}
                >
                    <input
                        ref={inputRef}
                        type="text"
                        className="w-full h-full bg-gray-900 text-white text-xs px-2 border-2 rounded outline-none shadow-2xl"
                        style={{ borderColor: themes[currentTheme]?.accent || '#4fd1c5' }}
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === ' ' || e.key === '-') {
                                e.preventDefault();
                                e.stopPropagation();
                                const trimmed = editValue.trim();
                                if (editingIdx !== null) {
                                    const current = lyrics[editingIdx];
                                    if (trimmed === '') {
                                        removeLyric(editingIdx);
                                        addLyricAt(current.timestamp);
                                    } else {
                                        updateLyric(editingIdx, { text: trimmed });
                                        addLyricAt(current.timestamp + current.duration);
                                    }
                                    setEditingIdx(null);
                                }
                            }
                        }}
                        onBlur={finishEditing}
                        autoFocus
                    />
                </div>
            )}
        </div>
    );
};
