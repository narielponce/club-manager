<template>
  <div class="card shadow-sm" style="width: 100%; max-width: 420px;">
    <div class="card-header text-center">
      <h2>Restablecer Contraseña</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="handleResetPassword">
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
            Restablecer Contraseña
          </button>
          <RouterLink to="/login" class="btn btn-link">Volver al Login</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute, RouterLink } from 'vue-router';
import { apiFetch } from '../services/api'; // Assuming apiFetch handles auth headers

const newPassword = ref('');
const confirmPassword = ref('');
const message = ref('');
const messageType = ref('');
const loading = ref(false);
const router = useRouter();
const route = useRoute();
const token = ref(null); // Will store the token from the URL

onMounted(() => {
  token.value = route.query.token;
  if (!token.value) {
    message.value = 'Token de restablecimiento de contraseña no encontrado.';
    messageType.value = 'alert-danger';
  }
});

const handleResetPassword = async () => {
  message.value = '';
  messageType.value = '';
  loading.value = true;

  if (!token.value) {
    message.value = 'Token de restablecimiento de contraseña no válido.';
    messageType.value = 'alert-danger';
    loading.value = false;
    return;
  }

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
    await apiFetch('/account/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token.value,
        new_password: newPassword.value,
      }),
    });

    message.value = 'Contraseña restablecida con éxito. Ya puedes iniciar sesión con tu nueva contraseña.';
    messageType.value = 'alert-success';
    newPassword.value = '';
    confirmPassword.value = '';
    setTimeout(() => {
      router.push('/login');
    }, 3000);

  } catch (err) {
    console.error('Error al restablecer la contraseña:', err);
    message.value = err.message || 'Ocurrió un error al restablecer la contraseña.';
    messageType.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Scoped styles for this component */
</style>
