import { ref } from 'vue'
import { apiFetch } from './api.js'
import { currentUser } from './user.js' // This will be the new user service for the expense manager
import { showSessionModal } from './session.js'

// --- Reactive State ---

// Retrieve tokens from localStorage
const storedTokens = JSON.parse(localStorage.getItem('tokens'));

// Reactive refs for tokens
export const accessToken = ref(storedTokens?.access_token || null);
export const refreshToken = ref(storedTokens?.refresh_token || null);


// --- Token Management Functions ---

/**
 * Saves both tokens to localStorage and updates the reactive refs.
 * @param {string} newAccessToken
 * @param {string} newRefreshToken
 */
export function saveTokens(newAccessToken, newRefreshToken) {
  const tokens = {
    access_token: newAccessToken,
    refresh_token: newRefreshToken,
  };
  localStorage.setItem('tokens', JSON.stringify(tokens));
  accessToken.value = newAccessToken;
  refreshToken.value = newRefreshToken;
}

/**
 * Clears authentication data from storage and state.
 */
export function clearAuthData() {
  localStorage.removeItem('tokens');
  accessToken.value = null;
  refreshToken.value = null;
  currentUser.value = null;
}


// --- Authentication Flow ---

export async function login(email, password) {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const data = await apiFetch('/token', {
    method: 'POST',
    body: formData
  });
  
  saveTokens(data.access_token, data.refresh_token);

  return data;
}

export function logout() {
  const wasLoggedIn = !!accessToken.value;
  clearAuthData();

  if (wasLoggedIn) {
    showSessionModal(
      "Sesión Finalizada",
      "Has cerrado sesión correctamente.",
      () => {
        window.location.href = '/login';
      }
    );
  } else {
    // If not logged in, just redirect
    window.location.href = '/login';
  }
}

export async function fetchCurrentUser() {
  if (accessToken.value) {
    try {
      // The endpoint will change in the new backend
      currentUser.value = await apiFetch('/users/me'); 
    } catch (error) {
      console.error("Failed to fetch user:", error);
      // The 401 handler in apiFetch will now handle the session expiration.
    }
  }
}