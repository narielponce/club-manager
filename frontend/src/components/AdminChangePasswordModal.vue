<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Cambiar Contraseña</h5>
          <button type="button" class="btn-close" @click="close"></button>
        </div>
        <div class="modal-body">
          <p class="text-muted">Establecer una nueva contraseña para <strong>{{ userEmail }}</strong>.</p>
          <p class="text-warning small">El usuario será forzado a cambiar esta contraseña en su próximo inicio de sesión.</p>
          <form @submit.prevent="submitPasswordChange">
            <div class="mb-3">
              <label for="new-password" class="form-label">Nueva Contraseña</label>
              <input type="text" id="new-password" class="form-control" v-model="newPassword" required />
            </div>
            <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
            <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="close">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="submitPasswordChange" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
            Guardar Contraseña
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { apiFetch } from '../services/api.js';

const props = defineProps({
  show: Boolean,
  userId: Number,
  userEmail: String
});

const emit = defineEmits(['close', 'password-changed']);

const newPassword = ref('');
const isSubmitting = ref(false);
const message = ref('');
const error = ref(null);

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset state when modal is shown
    newPassword.value = '';
    message.value = '';
    error.value = null;
    isSubmitting.value = false;
  }
});

const close = () => {
  emit('close');
};

const submitPasswordChange = async () => {
  if (!newPassword.value) {
    error.value = 'La contraseña no puede estar vacía.';
    return;
  }
  isSubmitting.value = true;
  error.value = null;
  message.value = '';

  try {
    await apiFetch(`/club/users/${props.userId}/change-password`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword.value }),
    });
    message.value = 'Contraseña cambiada con éxito.';
    emit('password-changed');
    setTimeout(close, 1500); // Close modal after 1.5s on success
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = e.message;
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>
