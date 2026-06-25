/**
 * api/socket.js
 * ──────────────
 * Shared Socket.IO client singleton.
 *
 * Fix: URL derivation no longer uses a fragile .replace('/api', '') call.
 * Instead we use a dedicated VITE_SOCKET_URL env var, falling back to
 * stripping the known /api path suffix safely via URL parsing.
 */
import { io } from 'socket.io-client';

function getSocketUrl() {
  // Prefer an explicit env var so there's no ambiguity.
  if (import.meta.env.VITE_SOCKET_URL) {
    return import.meta.env.VITE_SOCKET_URL;
  }
  // Fallback: strip /api from the end of VITE_API_URL (safe substring check).
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';
  return apiUrl.endsWith('/api') ? apiUrl.slice(0, -4) : apiUrl;
}

const socket = io(getSocketUrl(), {
  autoConnect:   true,
  reconnection:  true,
  transports:    ['websocket', 'polling'],
});

export default socket;
