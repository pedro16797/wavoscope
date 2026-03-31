import { useEffect } from 'react';
import { useStore } from '../store/useStore';

export const useAudioWebSocket = () => {
  const { fetchThemes, fetchStatus, fetchConfig, fetchLocales, fetchAudioDevices, updatePosition, setPlaying } = useStore();

  useEffect(() => {
    fetchThemes();
    fetchStatus();
    fetchConfig();
    fetchLocales();
    fetchAudioDevices();

    const isDev = window.location.origin.includes(':5173');
    const wsUrl = isDev
      ? `ws://${window.location.hostname}:8000/ws`
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.loaded !== undefined) {
            const wasLoaded = useStore.getState().loaded;
            const currentFilename = useStore.getState().filename;
            const currentCounter = (useStore.getState() as any).update_counter;

            if (data.loaded && (!wasLoaded
                || (data.filename && data.filename !== currentFilename)
                || (data.update_counter !== undefined && data.update_counter !== currentCounter))) {
                fetchStatus();
            }
        }
        updatePosition(data.position, data.loop_range);
        setPlaying(data.playing);

        // Update playback settings if they changed from another client
        const state = useStore.getState();
        if (data.loop_mode !== undefined && data.loop_mode !== state.loop_mode) {
            useStore.setState({ loop_mode: data.loop_mode });
        }
        if (data.metronome_enabled !== undefined && data.metronome_enabled !== state.metronome_enabled) {
            useStore.setState({ metronome_enabled: data.metronome_enabled });
        }
        if (data.speed !== undefined && data.speed !== state.speed) {
            useStore.setState({ speed: data.speed });
        }
        if (data.volume !== undefined && data.volume !== state.volume) {
            useStore.setState({ volume: data.volume });
        }
    };
    return () => ws.close();
  }, [fetchThemes, fetchStatus, fetchConfig, fetchLocales, fetchAudioDevices, updatePosition, setPlaying]);
};
