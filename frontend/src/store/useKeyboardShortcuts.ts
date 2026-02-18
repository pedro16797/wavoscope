import { useEffect } from 'react';
import { useStore } from './useStore';

export const useKeyboardShortcuts = () => {
  const { loaded, playing, controlPlayback, position, duration, speed, browseFile, showLyrics, setShowLyrics } = useStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!loaded && !['o', 'l'].includes(e.key.toLowerCase())) return;

      // Prevent default for handled shortcuts
      if ([' ', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 's', 'o', 'l', 'L'].includes(e.key)) {
        if (e.target instanceof HTMLInputElement) return; // Don't interrupt typing
      }

      switch (e.key) {
        case ' ':
          e.preventDefault();
          controlPlayback(playing ? 'pause' : 'play');
          break;
        case 'l':
        case 'L':
          setShowLyrics(!showLyrics);
          break;
        case 'ArrowLeft':
          controlPlayback('seek', Math.max(0, position - 0.1));
          break;
        case 'ArrowRight':
          controlPlayback('seek', Math.min(duration, position + 0.1));
          break;
        case 'ArrowUp':
          controlPlayback('set_speed', Math.min(4.0, speed + 0.1));
          break;
        case 'ArrowDown':
          controlPlayback('set_speed', Math.max(0.1, speed - 0.1));
          break;
        case 's':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            useStore.getState().saveProject();
          }
          break;
        case 'o':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            browseFile();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loaded, playing, controlPlayback, position, duration, speed, browseFile]);
};

