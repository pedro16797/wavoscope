import { useEffect } from 'react';
import { useStore } from '../store/useStore';

export const useTheme = () => {
  const { currentTheme, themes, ui_scale } = useStore();

  useEffect(() => {
    const theme = themes[currentTheme];
    if (theme) {
        document.documentElement.style.setProperty('--color-background', theme.background || '#1e1e1e');
        document.documentElement.style.setProperty('--color-surface', theme.surface || '#252525');
        document.documentElement.style.setProperty('--color-accent', theme.accent || '#00aaff');
        document.documentElement.style.setProperty('--color-grid', theme.grid || '#404040');
        document.documentElement.style.setProperty('--color-text', theme.text || '#e0e0e0');
        document.documentElement.style.setProperty('--ui-radius', theme.radius || '4px');
        document.documentElement.style.setProperty('--ui-font', theme.font || 'system-ui, sans-serif');
        document.documentElement.style.setProperty('--ui-border', theme.borderWidth || '1px');
    }
  }, [themes, currentTheme]);

  useEffect(() => {
    document.documentElement.style.fontSize = `${16 * ui_scale}px`;
    document.documentElement.style.setProperty('--ui-scale', ui_scale.toString());
  }, [ui_scale]);
};
