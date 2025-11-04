import { ref } from 'vue'
import { apiFetch } from './api.js'
import { currentUser } from './user.js'

// A simple reactive state for the token
export const token = ref(localStorage.getItem('token'))

export async function login(email, password) {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)

  // Use the generic apiFetch helper for the login request.
  // It will correctly resolve to /api/token.
  const data = await apiFetch('/token', {
    method: 'POST',
    body: formData
  })
  
  // Store the token and update reactive state
  localStorage.setItem('token', data.access_token)
  token.value = data.access_token

  // After getting token, fetch the user data
  await fetchCurrentUser()

  return data
}

export function logout() {
  localStorage.removeItem('token')
  token.value = null
  currentUser.value = null
  // Redirect to login to ensure a clean state
  window.location.href = '/login'
}

export async function fetchCurrentUser() {
  if (token.value) {
    try {
      currentUser.value = await apiFetch('/users/me')
    } catch (error) {
      console.error("Failed to fetch user:", error)
      // This can happen if the token is stale/invalid
      logout()
    }
  }
}
