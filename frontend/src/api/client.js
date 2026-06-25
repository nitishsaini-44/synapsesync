/**
 * api/client.js
 * ──────────────
 * Centralised Axios HTTP client.
 *
 * Fixes:
 * - H7: 401 response interceptor — automatically removes expired tokens and
 *        reloads to /login so the user isn't silently stuck in a broken state.
 * - Input: Bearer token is set via a default header when AuthContext calls
 *          setAuthHeader(token) — prevents mutation issues if the instance is shared.
 */
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const apiClient = axios.create({
  baseURL: BASE_URL,
});

// ── Auth header helper (called by AuthContext after login / on page load) ──────
export function setAuthHeader(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
}

// ── Response interceptor ───────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response.data,          // unwrap axios envelope → return server body directly

  (error) => {
    // H7: 401 means the JWT has expired or is invalid — log out and redirect.
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete apiClient.defaults.headers.common['Authorization'];
      // Use replace so the user can't navigate back to the broken page
      window.location.replace('/login');
    }
    return Promise.reject(error);
  }
);

// ── API functions ──────────────────────────────────────────────────────────────

// Auth
export const loginUser    = (email, password) =>
  apiClient.post('/auth/login',    { email, password });
export const registerUser = (name, email, password) =>
  apiClient.post('/auth/register', { name, email, password });

// Dashboard & Leads
export const getAnalytics = () =>
  apiClient.get('/analytics');
export const getLeads     = (category = 'all', page = 1, limit = 40) =>
  apiClient.get('/leads', { params: { category, page, limit } });

// AI Assistant
export const summarizeEmail = (message) =>
  apiClient.post('/summarize',      { message });
export const classifyLead   = (message) =>
  apiClient.post('/classify',       { message });
export const generateReply  = (message, category) =>
  apiClient.post('/generate-reply', { message, category });

// Integrations / Settings
export const getUserSettings    = () =>
  apiClient.get('/user/settings');
export const updateUserSettings = (settings) =>
  apiClient.put('/user/settings', settings);
export const getGoogleConnectUrl = () =>
  apiClient.get('/google/connect');
export const saveDiscordWebhook = (webhookUrl) =>
  apiClient.post('/discord/save', { webhook_url: webhookUrl });

export default apiClient;
