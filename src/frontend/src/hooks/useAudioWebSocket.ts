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

            if (data.loaded && (!wasLoaded || (data.filename && data.filename !== currentFilename))) {
                fetchStatus();
            }
        }
        updatePosition(data.position, data.loop_range);
        setPlaying(data.playing);
    };
    return () => ws.close();
  }, [fetchThemes, fetchStatus, fetchConfig, fetchLocales, fetchAudioDevices, updatePosition, setPlaying]);
};
