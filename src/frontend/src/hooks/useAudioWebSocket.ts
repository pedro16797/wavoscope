import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { WS_URL } from '../env';

const MAX_BACKOFF_MS = 10000;
const INITIAL_BACKOFF_MS = 500;

// Apply a single WebSocket status frame to the store. Exported for testing.
// Every field is guarded: a partial/heartbeat frame must never overwrite live
// state with `undefined` (which would turn position into NaN in every canvas).
export const handleWsMessage = (event: MessageEvent): void => {
  let data: any;
  try {
    data = JSON.parse(event.data);
  } catch {
    return; // ignore malformed frames instead of throwing inside the handler
  }
  if (!data || typeof data !== 'object') return;

  const store = useStore.getState();

  if (data.loaded !== undefined) {
    const wasLoaded = store.loaded;
    const currentFilename = store.filename;
    const currentCounter = (store as any).update_counter;
    if (data.loaded && (!wasLoaded
        || (data.filename && data.filename !== currentFilename)
        || (data.update_counter !== undefined && data.update_counter !== currentCounter))) {
      store.fetchStatus();
    }
  }

  if (data.position !== undefined) store.updatePosition(data.position, data.loop_range);
  if (data.playing !== undefined) store.setPlaying(data.playing);

  // Reflect playback settings changed by another client.
  if (data.loop_mode !== undefined && data.loop_mode !== store.loop_mode) {
    useStore.setState({ loop_mode: data.loop_mode });
  }
  if (data.metronome_enabled !== undefined && data.metronome_enabled !== store.metronome_enabled) {
    useStore.setState({ metronome_enabled: data.metronome_enabled });
  }
  if (data.speed !== undefined && data.speed !== store.speed) {
    useStore.setState({ speed: data.speed });
  }
  if (data.volume !== undefined && data.volume !== store.volume) {
    useStore.setState({ volume: data.volume });
  }
};

export const useAudioWebSocket = () => {
  useEffect(() => {
    useStore.getState().bootstrap();

    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let backoff = INITIAL_BACKOFF_MS;
    let stopped = false;
    let hasConnected = false;

    const scheduleReconnect = () => {
      if (stopped || reconnectTimer !== null) return;
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        if (!stopped) connect();
      }, backoff);
      backoff = Math.min(backoff * 2, MAX_BACKOFF_MS);
    };

    const connect = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        backoff = INITIAL_BACKOFF_MS;
        // After a reconnect we may have missed updates while offline; resync.
        if (hasConnected) useStore.getState().fetchStatus();
        hasConnected = true;
      };

      ws.onmessage = handleWsMessage;

      ws.onclose = () => scheduleReconnect();

      ws.onerror = () => {
        // onerror is followed by onclose, which drives the reconnect; ensure the
        // socket actually closes so that happens.
        try { ws?.close(); } catch { /* noop */ }
      };
    };

    connect();

    return () => {
      stopped = true;
      if (reconnectTimer !== null) clearTimeout(reconnectTimer);
      if (ws) {
        // Detach handlers so closing during cleanup doesn't schedule a reconnect.
        ws.onopen = null;
        ws.onclose = null;
        ws.onerror = null;
        ws.onmessage = null;
        try { ws.close(); } catch { /* noop */ }
      }
    };
  }, []);
};
