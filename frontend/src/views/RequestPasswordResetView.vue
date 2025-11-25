<template>
  <div class="card shadow-sm" style="width: 100%; max-width: 420px;">
    <div class="card-header text-center">
      <h2>Solicitar Restablecimiento de Contraseña</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="handleRequestReset">
        <div v-if="message" :class="['alert', messageType]">{{ message }}</div>
        
        <div class="mb-3">
          <label for="email" class="form-label">Email de usuario</label>
          <input
            type="email"
            id="email"
            class="form-control"
            v-model="email"
            required
            placeholder="admin@tuclub.com"
          />
          <div class="form-text">Ingresa tu email de usuario (el ficticio) para solicitar un enlace de restablecimiento.</div>
        </div>
        
        <div class="d-grid gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Enviar Enlace
          </button>
          <RouterLink to="/login" class="btn btn-link">Volver al Login</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { apiFetch } from '../services/api'; // Assuming apiFetch handles auth headers

const email = ref('');
const message = ref('');
const messageType = ref('');
const loading = ref(false);

const handleRequestReset = async () => {
  message.value = '';
  messageType.value = '';
  loading.value = true;

  try {
    await apiFetch('/account/request-password-reset', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: email.value }),
    });

    message.value = 'Si el email está registrado, se ha enviado un enlace de restablecimiento a tu email de recuperación.';
    messageType.value = 'alert-success';
    email.value = ''; // Clear email input

  } catch (err) {
    console.error('Error al solicitar el restablecimiento:', err);
    message.value = err.message || 'Ocurrió un error al solicitar el restablecimiento.';
    messageType.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Scoped styles for this component */
</style>
