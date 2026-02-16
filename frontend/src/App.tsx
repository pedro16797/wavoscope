import React, { useEffect } from 'react';
import { Group as PanelGroup, Panel, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { useStore } from './store/useStore';
import { useKeyboardShortcuts } from './store/useKeyboardShortcuts';
import { useAudioWebSocket } from './hooks/useAudioWebSocket';
import { useTheme } from './hooks/useTheme';
import { PlaybackBar } from './components/PlaybackBar';
import { WaveformView } from './components/WaveformView';
import { Spectrum } from './components/Spectrum';
import { SettingsDialog } from './components/SettingsDialog';
import { FlagDialog } from './components/FlagDialog';
import { ChordDialog } from './components/ChordDialog';

const App: React.FC = () => {
  const {
    showSettings, setShowSettings,
    editingFlagIdx, setEditingFlagIdx, flags,
    editingHarmonyFlagIdx, setEditingHarmonyFlagIdx, harmony_flags
  } = useStore();

  useKeyboardShortcuts();
  useAudioWebSocket();
  useTheme();

  useEffect(() => {
    // Expose setShowSettings to native menu
    (window as Window & { setShowSettings?: (show: boolean) => void }).setShowSettings = setShowSettings;
    (window as any).useStore = useStore;
  }, [setShowSettings]);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden text-sm select-none"
         style={{ backgroundColor: 'var(--color-background)', color: 'var(--color-text)' }}>
      <PlaybackBar />
      <div className="flex-1 relative min-h-0">
          <PanelGroup orientation="vertical" className="h-full">
            <Panel defaultSize={50} minSize={20}>
                <WaveformView />
            </Panel>
            <PanelResizeHandle className="h-1 bg-black/40 hover:bg-accent/50 transition-colors cursor-row-resize" />
            <Panel defaultSize={50} minSize={20}>
                <div className="flex flex-col h-full min-h-0">
                    <div className="h-6 border-b-[width:var(--ui-border)] flex items-center px-4 font-bold text-[10px] opacity-50 uppercase tracking-widest shrink-0 bg-surface"
                         style={{ borderBottomColor: 'var(--color-grid)' }}>
                      Spectrum Analyzer
                    </div>
                    <div className="flex-1 min-h-0">
                      <Spectrum />
                    </div>
                </div>
            </Panel>
          </PanelGroup>
      </div>

      {showSettings && <SettingsDialog onClose={() => setShowSettings(false)} />}
      {editingFlagIdx !== null && (
        <FlagDialog
          idx={editingFlagIdx}
          flag={flags[editingFlagIdx]}
          onClose={() => setEditingFlagIdx(null)}
        />
      )}
      {editingHarmonyFlagIdx !== null && (
        <ChordDialog
          idx={editingHarmonyFlagIdx}
          flag={harmony_flags[editingHarmonyFlagIdx]}
          onClose={() => setEditingHarmonyFlagIdx(null)}
        />
      )}
    </div>
  );
};

export default App;
