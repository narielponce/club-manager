import { ref } from 'vue'
import { apiFetch } from './api.js'
import { currentUser } from './user.js'
import { showSessionModal } from './session.js'
import { useRouter } from 'vue-router'


// A simple reactive state for the token
export const token = ref(localStorage.getItem('token'))

/**
 * Clears authentication data from storage and state.
 */
export function clearAuthData() {
  localStorage.removeItem('token')
  token.value = null
  currentUser.value = null
}

export async function login(email, password) {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)

  const data = await apiFetch('/token', {
    method: 'POST',
    body: formData
  })
  
  localStorage.setItem('token', data.access_token)
  token.value = data.access_token

  // fetchCurrentUser() will now be called by the app's main logic
  // after checking the force_password_change flag from the login response.

  return data
}

export function logout() {
  clearAuthData()
  showSessionModal(
    "Sesión Finalizada",
    "Has cerrado sesión correctamente.",
    () => {
      // Use a hard redirect to ensure all state is cleared
      window.location.href = '/login'
    }
  )
}

export async function fetchCurrentUser() {
  if (token.value) {
    try {
      currentUser.value = await apiFetch('/users/me')
    } catch (error) {
      console.error("Failed to fetch user:", error)
      // This can happen if the token is stale/invalid.
      // The 401 handler in apiFetch will now handle the UI part of this.
    }
  }
}
