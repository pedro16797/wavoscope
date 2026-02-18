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
        themes
    } = useStore();

    const [editingIdx, setEditingIdx] = useState<number | null>(null);
    const [editValue, setEditValue] = useState('');
    const [isAdding, setIsAdding] = useState(false);
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
            ctx.fillStyle = index === editingIdx ? (theme.accent || '#4fd1c5') + '66' : (theme.accent || '#4fd1c5') + '22';
            ctx.strokeStyle = theme.accent || '#4fd1c5';
            ctx.lineWidth = index === editingIdx ? 2 : 1.5;

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
    }, [lyrics, position, zoom, offset, editingIdx, themes, currentTheme]);

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
            if (clickedIdx !== -1) {
                setEditingIdx(clickedIdx);
                setEditValue(lyrics[clickedIdx].text);
                setIsAdding(false);
            } else {
                setEditingIdx(null);
            }
            return;
        }

        if (e.button === 0) { // Left click
            if (clickedIdx !== -1) {
                const startX = e.clientX;
                const startT = lyrics[clickedIdx].timestamp;
                let dragged = false;

                const onMouseMove = (moveEvent: MouseEvent) => {
                    dragged = true;
                    const dx = moveEvent.clientX - startX;
                    const dt = dx / zoom;
                    let newT = Math.round((startT + dt) * 100) / 100;

                    const prev = lyrics[clickedIdx - 1];
                    const next = lyrics[clickedIdx + 1];

                    if (prev && newT < prev.timestamp + prev.duration) {
                        newT = prev.timestamp + prev.duration;
                    }
                    if (next && newT + lyrics[clickedIdx].duration > next.timestamp) {
                        newT = next.timestamp - lyrics[clickedIdx].duration;
                    }
                    if (newT < 0) newT = 0;

                    moveLyric(clickedIdx, newT);
                };

                const onMouseUp = () => {
                    window.removeEventListener('mousemove', onMouseMove);
                    window.removeEventListener('mouseup', onMouseUp);
                    if (!dragged) {
                        // Regular click behavior if needed?
                        // Actually the user said right click for selection.
                    }
                };

                window.addEventListener('mousemove', onMouseMove);
                window.addEventListener('mouseup', onMouseUp);
            } else {
                setEditingIdx(null);
            }
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        if (!loaded || e.button !== 0) return;
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;
        const snappedT = Math.round(time * 100) / 100;

        const clickedIdx = lyrics.findIndex(l => time >= l.timestamp && time <= l.timestamp + l.duration);
        if (clickedIdx === -1) {
            addLyric({
                text: '',
                timestamp: snappedT,
                duration: 1.0
            }).then(() => {
                setTimeout(() => {
                    const updatedLyrics = useStore.getState().lyrics;
                    const idx = updatedLyrics.findIndex(l => Math.abs(l.timestamp - snappedT) < 0.01);
                    if (idx !== -1) {
                        setEditingIdx(idx);
                        setEditValue('');
                        setIsAdding(true);
                    }
                }, 50);
            });
        }
    };

    const startAddingAtPlayhead = useCallback(() => {
        const snappedTime = Math.round(position * 100) / 100;
        if (editingIdx !== null && isAdding) {
            const currentLyric = lyrics[editingIdx];
            const newDuration = Math.max(0.1, snappedTime - currentLyric.timestamp);
            updateLyric(editingIdx, { ...currentLyric, duration: newDuration, text: editValue });

            addLyric({
                text: '',
                timestamp: snappedTime,
                duration: 1.0
            }).then(() => {
                setTimeout(() => {
                    const updatedLyrics = useStore.getState().lyrics;
                    const idx = updatedLyrics.findIndex(l => Math.abs(l.timestamp - snappedTime) < 0.01);
                    if (idx !== -1) {
                        setEditingIdx(idx);
                        setEditValue('');
                        setIsAdding(true);
                    }
                }, 50);
            });
        } else {
            addLyric({
                text: '',
                timestamp: snappedTime,
                duration: 1.0
            }).then(() => {
                setTimeout(() => {
                    const updatedLyrics = useStore.getState().lyrics;
                    const idx = updatedLyrics.findIndex(l => Math.abs(l.timestamp - snappedTime) < 0.01);
                    if (idx !== -1) {
                        setEditingIdx(idx);
                        setEditValue('');
                        setIsAdding(true);
                    }
                }, 50);
            });
        }
    }, [editingIdx, isAdding, lyrics, position, editValue, addLyric, updateLyric]);

    const finishEditing = useCallback(() => {
        if (editingIdx !== null) {
            if (editValue.trim() === '') {
                removeLyric(editingIdx);
            } else {
                updateLyric(editingIdx, { text: editValue });
            }
            setEditingIdx(null);
            setIsAdding(false);
        }
    }, [editingIdx, editValue, updateLyric, removeLyric]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (editingIdx === null) {
                if (e.shiftKey && e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prev = [...lyrics].reverse().find(l => l.timestamp < position - 0.1);
                    if (prev) controlPlayback('seek', prev.timestamp);
                } else if (e.shiftKey && e.key === 'ArrowRight') {
                    e.preventDefault();
                    const next = lyrics.find(l => l.timestamp > position + 0.1);
                    if (next) controlPlayback('seek', next.timestamp);
                }
                return;
            }

            if (e.key === 'Enter') {
                finishEditing();
            } else if (e.key === 'Escape') {
                setEditingIdx(null);
                setIsAdding(false);
            } else if (e.key === 'ArrowLeft' && !e.shiftKey && (e.target as HTMLElement).tagName !== 'INPUT') {
                let newT = lyrics[editingIdx].timestamp - 0.1;
                const prev = lyrics[editingIdx - 1];
                if (prev && newT < prev.timestamp + prev.duration) newT = prev.timestamp + prev.duration;
                moveLyric(editingIdx, Math.max(0, newT));
            } else if (e.key === 'ArrowRight' && !e.shiftKey && (e.target as HTMLElement).tagName !== 'INPUT') {
                let newT = lyrics[editingIdx].timestamp + 0.1;
                const next = lyrics[editingIdx + 1];
                if (next && newT + lyrics[editingIdx].duration > next.timestamp) newT = next.timestamp - lyrics[editingIdx].duration;
                moveLyric(editingIdx, newT);
            } else if (e.key === 'ArrowUp' && (e.target as HTMLElement).tagName !== 'INPUT') {
                let newD = lyrics[editingIdx].duration + 0.1;
                const next = lyrics[editingIdx + 1];
                if (next && lyrics[editingIdx].timestamp + newD > next.timestamp) newD = next.timestamp - lyrics[editingIdx].timestamp;
                updateLyric(editingIdx, { duration: newD });
            } else if (e.key === 'ArrowDown' && (e.target as HTMLElement).tagName !== 'INPUT') {
                updateLyric(editingIdx, { duration: Math.max(0.1, lyrics[editingIdx].duration - 0.1) });
            } else if (e.code === 'Space' && isAdding) {
                e.preventDefault();
                startAddingAtPlayhead();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [editingIdx, lyrics, position, editValue, isAdding, startAddingAtPlayhead, finishEditing, controlPlayback, moveLyric, updateLyric, loaded]);

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
                        className="w-full h-full bg-gray-800 text-white text-xs px-1 border border-cyan-400 rounded outline-none shadow-lg"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={finishEditing}
                        autoFocus
                    />
                </div>
            )}
        </div>
    );
};
