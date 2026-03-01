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

    const ws = new WebSocket('ws://127.0.0.1:8000/ws');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updatePosition(data.position, data.loop_range);
        setPlaying(data.playing);
    };
    return () => ws.close();
  }, [fetchThemes, fetchStatus, fetchConfig, fetchLocales, fetchAudioDevices, updatePosition, setPlaying]);
};
