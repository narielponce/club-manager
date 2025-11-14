<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/auth.js'
import { showSessionModal } from '../services/session.js'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleSubmit = async () => {
  try {
    await login(email.value, password.value)
    router.push('/') // Redirect to dashboard on success
  } catch (err) {
    // Show a modal on login failure
    showSessionModal(
      "Error de Autenticación",
      "Usuario o contraseña incorrecto.",
      () => {} // Empty callback, just closes the modal
    )
  }
}
</script>

<template>
  <div class="card shadow-sm" style="width: 100%; max-width: 420px;">
    <div class="card-header text-center">
      <h2>Iniciar Sesión</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input
            type="email"
            id="email"
            class="form-control"
            v-model="email"
            required
          />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Contraseña</label>
          <input
            type="password"
            id="password"
            class="form-control"
            v-model="password"
            required
          />
        </div>
        <div class="d-grid">
          <button type="submit" class="btn btn-primary">Login</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* The layout for the login page should not include the main dashboard sidebar */
/* We might need to adjust App.vue to conditionally render the layout */
</style>
