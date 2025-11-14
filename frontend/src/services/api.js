import { token, clearAuthData } from './auth.js';
import { showSessionModal } from './session.js';

// Custom error class for session expiration
class SessionExpiredError extends Error {
  constructor(message) {
    super(message);
    this.name = "SessionExpiredError";
  }
}

const API_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function apiFetch(endpoint, options = {}) {
  const headers = { ...options.headers };

  if (token.value) {
    headers['Authorization'] = `Bearer ${token.value}`;
  }

  // Do NOT set Content-Type if body is FormData; the browser does it automatically
  // with the correct boundary.
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (response.status === 401) {
    // Token is invalid or expired. Clear auth data and show the session modal.
    clearAuthData();
    showSessionModal(
      "Sesión Expirada",
      "Tu sesión ha expirado. Por favor, inicia sesión de nuevo.",
      () => { window.location.href = '/login'; }
    );
    // Throw a specific error type that calling components can ignore
    throw new SessionExpiredError('Session expired. Modal displayed.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API request failed with status ${response.status}`);
  }

  // For DELETE requests with 204 No Content, response.json() will fail
  if (response.status === 204) {
    return null;
  }

  return response.json();
}
