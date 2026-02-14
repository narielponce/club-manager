import { accessToken, refreshToken, saveTokens, clearAuthData } from './auth.js';
import { showSessionModal } from './session.js';

// Custom error class for session expiration
class SessionExpiredError extends Error {
  constructor(message) {
    super(message);
    this.name = "SessionExpiredError";
  }
}

// --- Refresh Logic ---

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

async function refreshAuthToken() {
  if (!refreshToken.value) {
    return Promise.reject(new Error("No refresh token available"));
  }

  try {
    const response = await fetch(`${API_URL}/token/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken.value }),
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const newTokens = await response.json();
    saveTokens(newTokens.access_token, newTokens.refresh_token);
    return newTokens.access_token;
  } catch (error) {
    console.error("Token refresh failed:", error);
    // If refresh fails, the session is truly over
    clearAuthData();
    showSessionModal(
      "Sesión Expirada",
      "Tu sesión ha expirado. Por favor, inicia sesión de nuevo.",
      () => { window.location.href = '/login'; }
    );
    throw new SessionExpiredError('Session expired. Modal displayed.');
  }
}


// --- API Fetch Wrapper ---

const API_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function apiFetch(endpoint, options = {}) {
  // Wait for any ongoing refresh to complete
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      failedQueue.push({ resolve, reject });
    })
    .then(newAccessToken => {
      const newOptions = { ...options };
      newOptions.headers = { ...newOptions.headers, 'Authorization': `Bearer ${newAccessToken}` };
      return apiFetch(endpoint, newOptions); // Retry with new token
    });
  }

  const makeRequest = async (token) => {
    const headers = { ...options.headers };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    const config = { ...options, headers };
    return fetch(`${API_URL}${endpoint}`, config);
  };

  let response = await makeRequest(accessToken.value);

  if (response.status === 401) {
    if (isRefreshing) {
      // If another request is already refreshing, queue this one.
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(newAccessToken => {
        return makeRequest(newAccessToken);
      });
    }

    isRefreshing = true;
    try {
      const newAccessToken = await refreshAuthToken();
      processQueue(null, newAccessToken);
      response = await makeRequest(newAccessToken); // Retry the original request
    } catch (error) {
      processQueue(error, null);
      throw error; // Rethrow session expired error
    } finally {
      isRefreshing = false;
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let errorMessage = `API request failed with status ${response.status}`;
    if (typeof errorData.detail === 'string') {
      errorMessage = errorData.detail;
    } else if (typeof errorData.detail === 'object') {
      errorMessage = JSON.stringify(errorData.detail, null, 2);
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}