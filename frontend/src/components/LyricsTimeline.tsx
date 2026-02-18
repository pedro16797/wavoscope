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
        duration,
        currentTime,
        setCurrentTime,
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

        const width = canvas.width / (window.devicePixelRatio || 1);
        const dpr = window.devicePixelRatio || 1;
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
            // Using a slightly more vibrant fill for the non-editing state to make it "pop"
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

            // Truncate text if it doesn't fit
            let text = lyric.text;
            const metrics = ctx.measureText(text);
            if (metrics.width > w - 10) {
                // simple truncation
                text = text.substring(0, Math.max(1, Math.floor((w-10)/8))) + '...';
            }

            ctx.fillText(text, x + w / 2, height / 2);
        });

        // Draw playhead
        const playheadX = (currentTime - offset) * zoom;
        if (playheadX >= 0 && playheadX <= width) {
            ctx.strokeStyle = theme.playhead || '#f56565';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(playheadX, 0);
            ctx.lineTo(playheadX, height);
            ctx.stroke();
        }
    }, [lyrics, currentTime, zoom, offset, editingIdx, themes, currentTheme]);

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

    const handleCanvasClick = (e: React.MouseEvent) => {
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        // Check if clicked on a lyric
        const clickedIdx = lyrics.findIndex(l => time >= l.timestamp && time <= l.timestamp + l.duration);
        if (clickedIdx !== -1) {
            setEditingIdx(clickedIdx);
            setEditValue(lyrics[clickedIdx].text);
            setIsAdding(false);
        } else {
            setEditingIdx(null);
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        const rect = canvasRef.current?.getBoundingClientRect();
        if (!rect) return;
        const x = e.clientX - rect.left;
        const time = offset + x / zoom;

        const clickedIdx = lyrics.findIndex(l => time >= l.timestamp && time <= l.timestamp + l.duration);
        if (clickedIdx === -1) {
            // Add new lyric at this time
            addLyric({
                text: '',
                timestamp: Math.round(time * 100) / 100,
                duration: 1.0
            });
            setEditingIdx(lyrics.length);
            setEditValue('');
            setIsAdding(true);
        }
    };

    const startAddingAtPlayhead = useCallback(() => {
        const snappedTime = Math.round(currentTime * 100) / 100;
        // If we are currently editing/adding a word, finish it
        if (editingIdx !== null && isAdding) {
            const currentLyric = lyrics[editingIdx];
            const newDuration = Math.max(0.1, snappedTime - currentLyric.timestamp);
            updateLyric(editingIdx, { ...currentLyric, duration: newDuration, text: editValue });

            // Start NEXT word
            addLyric({
                text: '',
                timestamp: snappedTime,
                duration: 1.0
            });
            setEditingIdx(lyrics.length);
            setEditValue('');
            setIsAdding(true);
        } else {
            // Start FIRST word
            addLyric({
                text: '',
                timestamp: snappedTime,
                duration: 1.0
            });
            setEditingIdx(lyrics.length);
            setEditValue('');
            setIsAdding(true);
        }
    }, [editingIdx, isAdding, lyrics, currentTime, editValue, addLyric, updateLyric]);

    const finishEditing = useCallback(() => {
        if (editingIdx !== null) {
            if (editValue.trim() === '' && isAdding) {
                removeLyric(editingIdx);
            } else {
                updateLyric(editingIdx, { text: editValue });
            }
            setEditingIdx(null);
            setIsAdding(false);
        }
    }, [editingIdx, editValue, updateLyric, removeLyric, isAdding]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (editingIdx === null) {
                // Navigation shortcuts
                if (e.shiftKey && e.key === 'ArrowLeft') {
                    e.preventDefault();
                    // Jump to previous word
                    const prevIdx = [...lyrics].reverse().find(l => l.timestamp < currentTime - 0.1);
                    if (prevIdx) setCurrentTime(prevIdx.timestamp);
                } else if (e.shiftKey && e.key === 'ArrowRight') {
                    e.preventDefault();
                    // Jump to next word
                    const nextIdx = lyrics.find(l => l.timestamp > currentTime + 0.1);
                    if (nextIdx) setCurrentTime(nextIdx.timestamp);
                } else if (e.code === 'Space' && (e.target as HTMLElement).tagName !== 'INPUT') {
                    if (loaded) {
                        e.preventDefault();
                        startAddingAtPlayhead();
                    }
                }
                return;
            }

            // If editing
            if (e.key === 'Enter') {
                finishEditing();
            } else if (e.key === 'Escape') {
                setEditingIdx(null);
                setIsAdding(false);
            } else if (e.key === 'ArrowLeft' && !e.shiftKey && (e.target as HTMLElement).tagName !== 'INPUT') {
                moveLyric(editingIdx, lyrics[editingIdx].timestamp - 0.1);
            } else if (e.key === 'ArrowRight' && !e.shiftKey && (e.target as HTMLElement).tagName !== 'INPUT') {
                moveLyric(editingIdx, lyrics[editingIdx].timestamp + 0.1);
            } else if (e.key === 'ArrowUp' && (e.target as HTMLElement).tagName !== 'INPUT') {
                updateLyric(editingIdx, { duration: lyrics[editingIdx].duration + 0.1 });
            } else if (e.key === 'ArrowDown' && (e.target as HTMLElement).tagName !== 'INPUT') {
                updateLyric(editingIdx, { duration: Math.max(0.1, lyrics[editingIdx].duration - 0.1) });
            } else if (e.code === 'Space' && isAdding) {
                // Finish this word and start next
                e.preventDefault();
                startAddingAtPlayhead();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [editingIdx, lyrics, currentTime, editValue, isAdding, startAddingAtPlayhead, finishEditing, setCurrentTime, moveLyric, updateLyric, loaded]);

    useEffect(() => {
        if (editingIdx !== null && inputRef.current) {
            inputRef.current.focus();
        }
    }, [editingIdx]);

    return (
        <div ref={containerRef} className="relative w-full h-8 select-none bg-surface border-b" style={{ borderBottomColor: 'var(--color-grid)' }}>
            <canvas
                ref={canvasRef}
                onClick={handleCanvasClick}
                onDoubleClick={handleDoubleClick}
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
