import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Group as PanelGroup, Panel, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { useStore } from './store/useStore';
import { useKeyboardShortcuts } from './store/useKeyboardShortcuts';
import { useAudioWebSocket } from './hooks/useAudioWebSocket';
import { useTheme } from './hooks/useTheme';
import { PlaybackBar } from './components/PlaybackBar';
import { WaveformView } from './components/WaveformView';
import { SpectrumView } from './components/SpectrumView';
import { SettingsDialog } from './components/SettingsDialog';
import { FlagDialog } from './components/FlagDialog';
import { ChordDialog } from './components/ChordDialog';
import { ProgressDialog } from './components/ProgressDialog';
import { PlaylistDialog } from './components/PlaylistDialog';

const App: React.FC = () => {
  const { t } = useTranslation();
  const {
    showSettings, setShowSettings,
    showPlaylistDialog, setShowPlaylistDialog,
    editingFlagIdx, setEditingFlagIdx, flags,
    editingHarmonyFlagIdx, setEditingHarmonyFlagIdx, harmony_flags,
    isRemote, loaded
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
        {!loaded ? (
            <div className="h-full flex flex-col items-center justify-center opacity-40">
                <div className="text-4xl mb-4">🎵</div>
                <div className="text-lg font-bold tracking-widest uppercase">{t('common.drop_file_to_start') || 'Drop an audio file to begin'}</div>
            </div>
        ) : isRemote ? (
          <WaveformView />
        ) : (
          <PanelGroup orientation="vertical" className="h-full">
            <Panel defaultSize={50} minSize={20}>
                <WaveformView />
            </Panel>
            <PanelResizeHandle className="h-1 bg-black/40 hover:bg-accent/50 transition-colors cursor-row-resize" />
            <Panel defaultSize={50} minSize={20}>
                <SpectrumView />
            </Panel>
          </PanelGroup>
        )}
      </div>

      {showSettings && <SettingsDialog onClose={() => setShowSettings(false)} />}
      {showPlaylistDialog && <PlaylistDialog onClose={() => setShowPlaylistDialog(false)} />}
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
      <ProgressDialog />
    </div>
  );
};

export default App;
