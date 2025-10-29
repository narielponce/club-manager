import { ref } from 'vue'
import { apiFetch } from './api.js'
import { currentUser } from './user.js'

// A simple reactive state for the token
export const token = ref(localStorage.getItem('token'))

export async function login(email, password) {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)

  // Use raw fetch for the login request itself
  const response = await fetch(`http://127.0.0.1:8000/token`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to login')
  }

  const data = await response.json()
  
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
