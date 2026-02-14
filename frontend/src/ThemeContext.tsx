import React, { createContext, useContext, useEffect, useState } from 'react';

const API_URL = 'http://127.0.0.1:8000';

interface Theme {
  accent: string;
  background: string;
  surface: string;
  grid: string;
  text: string;
  textSecondary: string;
  keyWhite: string;
  keyBlack: string;
  waveform: string;
  spectrum: string;
  flagRhythm: string;
  flagHarmony: string;
}

interface ThemeContextType {
  theme: Theme | null;
  currentThemeName: string;
  setTheme: (name: string) => Promise<void>;
  themes: string[];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeData] = useState<Theme | null>(null);
  const [currentThemeName, setCurrentThemeName] = useState('dark');
  const [themes, setThemes] = useState<string[]>([]);

  useEffect(() => {
    fetch(`${API_URL}/themes`).then(res => res.json()).then(setThemes);
    fetchTheme('dark');
  }, []);

  const fetchTheme = async (name: string) => {
    const res = await fetch(`${API_URL}/themes/${name}`);
    const data = await res.json();
    setThemeData(data);
    setCurrentThemeName(name);
    applyTheme(data);
  };

  const applyTheme = (t: Theme) => {
    const root = document.documentElement;
    Object.entries(t).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
  };

  const setTheme = async (name: string) => {
    await fetchTheme(name);
    await fetch(`${API_URL}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme: name })
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, currentThemeName, setTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
