import React, { useEffect } from 'react';
import { Group as PanelGroup, Panel, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { useStore } from './store/useStore';
import { useKeyboardShortcuts } from './store/useKeyboardShortcuts';
import { PlaybackBar } from './components/PlaybackBar';
import { WaveformView } from './components/WaveformView';
import { Spectrum } from './components/Spectrum';

const App: React.FC = () => {
  const { fetchThemes, fetchStatus, updatePosition, setPlaying, currentTheme, themes } = useStore();
  const theme = themes[currentTheme] || {};

  useKeyboardShortcuts();

  useEffect(() => {
    fetchThemes();
    fetchStatus();

    const ws = new WebSocket('ws://127.0.0.1:8000/ws');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updatePosition(data.position);
        setPlaying(data.playing);
    };
    return () => ws.close();
  }, [fetchThemes, fetchStatus, updatePosition, setPlaying]);

  useEffect(() => {
    if (theme) {
        document.documentElement.style.setProperty('--color-background', theme.background || '#1e1e1e');
        document.documentElement.style.setProperty('--color-surface', theme.surface || '#252525');
        document.documentElement.style.setProperty('--color-accent', theme.accent || '#00aaff');
        document.documentElement.style.setProperty('--color-grid', theme.grid || '#404040');
        document.documentElement.style.setProperty('--color-text', theme.text || '#e0e0e0');
    }
  }, [theme]);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden text-sm select-none"
         style={{ backgroundColor: 'var(--color-background)', color: 'var(--color-text)' }}>
      <PlaybackBar />
      <div className="flex-1 relative">
          <PanelGroup orientation="vertical">
            <Panel defaultSize={50} minSize={20}>
                <WaveformView />
            </Panel>
            <PanelResizeHandle className="h-1 bg-black/40 hover:bg-accent/50 transition-colors cursor-row-resize" />
            <Panel defaultSize={50} minSize={20}>
                <div className="flex flex-col h-full">
                    <div className="h-6 border-b flex items-center px-4 font-bold text-[10px] opacity-50 uppercase tracking-widest"
                         style={{ backgroundColor: 'var(--color-surface)', borderBottomColor: 'var(--color-grid)' }}>
                      Spectrum Analyzer
                    </div>
                    <div className="flex-1">
                      <Spectrum />
                    </div>
                </div>
            </Panel>
          </PanelGroup>
      </div>
    </div>
  );
};

export default App;
