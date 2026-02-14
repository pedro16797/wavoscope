import { useEffect } from 'react';

export function useKeyboardShortcuts(actions: { [key: string]: () => void }) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      let key = e.key;
      if (e.ctrlKey) key = 'Ctrl+' + key;
      if (e.shiftKey) key = 'Shift+' + key;

      if (actions[key]) {
        e.preventDefault();
        actions[key]();
      } else if (key === ' ') {
        e.preventDefault();
        actions['Space']?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [actions]);
}
