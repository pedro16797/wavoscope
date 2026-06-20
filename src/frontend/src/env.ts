// Centralized dev-host detection and backend URLs.
// In dev the Vite server runs on :5173/:5174 and talks to the backend on :8000;
// in production the frontend is served by the backend itself (same origin).
const DEV_PORTS = [':5173', ':5174'];

export const isDev = DEV_PORTS.some((p) => window.location.origin.includes(p));

export const API_BASE = isDev ? `http://${window.location.hostname}:8000` : '';

export const WS_URL = isDev
  ? `ws://${window.location.hostname}:8000/ws`
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
