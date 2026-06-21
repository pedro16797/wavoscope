// Centralized dev-host detection, backend URLs, and remote-token handling.
// In dev the Vite server runs on :5173/:5174 and talks to the backend on :8000;
// in production the frontend is served by the backend itself (same origin).
const DEV_PORTS = [':5173', ':5174'];

export const isDev = DEV_PORTS.some((p) => window.location.origin.includes(p));

export const API_BASE = isDev ? `http://${window.location.hostname}:8000` : '';

// Remote devices open a URL containing ?token=<secret>. Persist it for the
// session so it survives navigation/refresh, and attach it to API/WebSocket
// calls. The host's own browser loads without a token (it's loopback and always
// authorized), so this stays empty there.
function readRemoteToken(): string {
  try {
    const fromUrl = new URLSearchParams(window.location.search).get('token');
    if (fromUrl) {
      sessionStorage.setItem('wavoscope_token', fromUrl);
      return fromUrl;
    }
    return sessionStorage.getItem('wavoscope_token') || '';
  } catch {
    return '';
  }
}

export const REMOTE_TOKEN = readRemoteToken();

const WS_HOST = isDev
  ? `ws://${window.location.hostname}:8000/ws`
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

export const WS_URL = REMOTE_TOKEN
  ? `${WS_HOST}?token=${encodeURIComponent(REMOTE_TOKEN)}`
  : WS_HOST;
