import { token, logout } from './auth.js';

const API_URL = 'http://127.0.0.1:8000';

export async function apiFetch(endpoint, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  if (token.value) {
    defaultHeaders['Authorization'] = `Bearer ${token.value}`;
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  // For GET requests, body should not be included
  if (config.method === 'GET' || !config.method) {
    delete config.body;
  }

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
