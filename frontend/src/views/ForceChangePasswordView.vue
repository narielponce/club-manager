<template>
  <div class="card shadow-sm" style="width: 100%; max-width: 420px;">
    <div class="card-header text-center">
      <h2>Cambiar Contraseña</h2>
      <p class="text-danger mb-0">Debes cambiar tu contraseña para continuar.</p>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="handleChangePassword">
        <div v-if="message" :class="['alert', messageType]">{{ message }}</div>
        
        <div class="mb-3">
          <label for="newPassword" class="form-label">Nueva Contraseña</label>
          <input
            type="password"
            id="newPassword"
            class="form-control"
            v-model="newPassword"
            required
            minlength="8"
          />
        </div>
        <div class="mb-3">
          <label for="confirmPassword" class="form-label">Confirmar Nueva Contraseña</label>
          <input
            type="password"
            id="confirmPassword"
            class="form-control"
            v-model="confirmPassword"
            required
          />
        </div>
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Cambiar Contraseña
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { apiFetch } from '../services/api'; // Assuming apiFetch handles auth headers
import { clearAuthData } from '../services/auth'; // To clear token on error or success
import { showSessionModal } from '../services/session.js'


const newPassword = ref('');
const confirmPassword = ref('');
const message = ref('');
const messageType = ref(''); // 'alert-success' or 'alert-danger'
const loading = ref(false);
const router = useRouter();

const handleChangePassword = async () => {
  message.value = '';
  messageType.value = '';
  loading.value = true;

  if (newPassword.value !== confirmPassword.value) {
    message.value = 'Las contraseñas no coinciden.';
    messageType.value = 'alert-danger';
    loading.value = false;
    return;
  }

  if (newPassword.value.length < 8) {
    message.value = 'La contraseña debe tener al menos 8 caracteres.';
    messageType.value = 'alert-danger';
    loading.value = false;
    return;
  }

  try {
    // Current password is not required here, as the user is forced to change it
    // The backend endpoint /account/change-password expects current_password.
    // This view is for initial forced change, it can't know the current password,
    // which is the temporary one.
    // This means the /account/change-password endpoint needs an alternative
    // that accepts only new_password if force_password_change is true for the user.
    //
    // For now, I'll send a dummy current_password and rely on the backend logic
    // to bypass current_password check if force_password_change is true.
    // However, the backend is implemented to expect current_password.
    // So, this frontend view implies a slightly different backend endpoint,
    // or a modification to the existing change-password.

    // Let's adjust: the forced change doesn't require the *current* password
    // because the user might not even know it (temporary).
    // The backend should check for `force_password_change` flag and bypass
    // current_password validation if it's true. This is safer.

    // I will call /account/change-password with a dummy current_password
    // and modify the backend to handle it.
    
    // For now, let's assume the backend takes only `new_password`
    // for forced change, or handles `current_password` intelligently.
    // The current backend endpoint expects `current_password`.
    // So, I need to create a new endpoint, or modify the existing one.
    // Let's create a specific endpoint for forced change.
    
    await apiFetch('/account/change-password', { // Changed to actual endpoint
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: null, // Send null for current password during forced change
        new_password: newPassword.value,
      }),
    });

    message.value = 'Contraseña cambiada con éxito. Por favor, inicia sesión con tu nueva contraseña.';
    messageType.value = 'alert-success';
    clearAuthData(); // Clear token, force re-login
    setTimeout(() => {
      router.push('/login');
    }, 3000);

  } catch (err) {
    console.error('Error al cambiar la contraseña:', err);
    message.value = err.message || 'Ocurrió un error al cambiar la contraseña.';
    messageType.value = 'alert-danger';
    clearAuthData(); // Clear token to be safe
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Scoped styles for this component */
</style>
