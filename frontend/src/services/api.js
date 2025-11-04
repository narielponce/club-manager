import { token, logout } from './auth.js';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

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
    // Token is invalid or expired, log the user out
    logout();
    throw new Error('Session expired. Please log in again.');
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
