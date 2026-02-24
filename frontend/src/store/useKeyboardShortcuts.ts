import { useEffect } from 'react';
import { useStore } from './useStore';

export const useKeyboardShortcuts = () => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const state = useStore.getState();
      const {
        loaded, playing, controlPlayback, position, duration, speed, browseFile, cycleLoopMode,
        selectedLyricIdx, setSelectedLyricIdx, showSettings, setShowSettings, saveProject, exportMusicXML,
        octave_shift, setOctaveShift, fft_window, setFFTWindow, metronome_enabled, updateMetronome,
        editingFlagIdx, editingHarmonyFlagIdx, setEditingFlagIdx, setEditingHarmonyFlagIdx,
        addFlag, addHarmonyFlag, removeFlag, removeHarmonyFlag, removeLyric,
        updateFilter
      } = state;

      const isInput = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || (e.target as HTMLElement).isContentEditable;
      if (isInput) return;

      const allowedWhenNotLoaded = ['o', 'escape'];
      if (!loaded && !allowedWhenNotLoaded.includes(e.key.toLowerCase())) return;

      // Handle Escape
      if (e.key === 'Escape') {
          if (editingFlagIdx !== null) {
              setEditingFlagIdx(null);
              return;
          }
          if (editingHarmonyFlagIdx !== null) {
              setEditingHarmonyFlagIdx(null);
              return;
          }
          setShowSettings(!showSettings);
          return;
      }

      if (e.key === 'L' && e.shiftKey) {
        e.preventDefault();
        setSelectedLyricIdx(null);
        return;
      }

      // Handle Delete / Backspace
      if (e.key === 'Delete' || e.key === 'Backspace') {
          if (editingFlagIdx !== null) {
              e.preventDefault();
              removeFlag(editingFlagIdx);
              setEditingFlagIdx(null);
              return;
          }
          if (editingHarmonyFlagIdx !== null) {
              e.preventDefault();
              removeHarmonyFlag(editingHarmonyFlagIdx);
              setEditingHarmonyFlagIdx(null);
              return;
          }
          if (selectedLyricIdx !== null) {
              e.preventDefault();
              removeLyric(selectedLyricIdx);
              setSelectedLyricIdx(null);
              return;
          }
      }

      // Add Rhythm Flag: B
      if (e.key.toLowerCase() === 'b' && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          addFlag(position).then((res: any) => {
              if (res && res.idx !== undefined && res.idx !== -1) setEditingFlagIdx(res.idx);
          });
          return;
      }

      // Add Harmony Flag: H
      if (e.key.toLowerCase() === 'h' && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          addHarmonyFlag(position).then((res: any) => {
              if (res && res.idx !== undefined && res.idx !== -1) setEditingHarmonyFlagIdx(res.idx);
          });
          return;
      }

      // Stop: Shift + Space
      if (e.key === ' ' && e.shiftKey) {
          e.preventDefault();
          controlPlayback('stop');
          return;
      }

      // Metronome: M
      if (e.key.toLowerCase() === 'm' && !e.ctrlKey && !e.metaKey) {
          updateMetronome(!metronome_enabled);
          return;
      }

      // Filter: F / Shift+F
      if (e.key.toLowerCase() === 'f' && !e.ctrlKey && !e.metaKey) {
          if (e.shiftKey) {
              const { filter_high_enabled } = useStore.getState();
              updateFilter({ high_enabled: !filter_high_enabled, enabled: true });
          } else {
              const { filter_low_enabled } = useStore.getState();
              updateFilter({ low_enabled: !filter_low_enabled, enabled: true });
          }
          return;
      }

      switch (e.key) {
        case 'Tab':
          e.preventDefault();
          cycleLoopMode();
          break;
        case ' ':
          e.preventDefault();
          controlPlayback(playing ? 'pause' : 'play');
          break;
        case 'ArrowLeft':
          if (e.shiftKey) {
              setOctaveShift(octave_shift - 1);
          } else {
              controlPlayback('seek', Math.max(0, position - 0.1));
          }
          break;
        case 'ArrowRight':
          if (e.shiftKey) {
              setOctaveShift(octave_shift + 1);
          } else {
              controlPlayback('seek', Math.min(duration, position + 0.1));
          }
          break;
        case 'ArrowUp':
          if (e.shiftKey) {
              setFFTWindow(Math.min(1.0, fft_window + 0.05));
          } else {
              controlPlayback('set_speed', Math.min(4.0, speed + 0.1));
          }
          break;
        case 'ArrowDown':
          if (e.shiftKey) {
              setFFTWindow(Math.max(0.05, fft_window - 0.05));
          } else {
              controlPlayback('set_speed', Math.max(0.1, speed - 0.1));
          }
          break;
        case 's':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            saveProject();
          }
          break;
        case 'o':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            browseFile();
          }
          break;
        case 'e':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            exportMusicXML();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
};

