<script setup>
import { ref, watch } from 'vue';
import { apiFetch } from '../services/api.js';

const props = defineProps({
  show: Boolean,
  user: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close', 'user-updated']);

const form = ref({
  role: '',
  recovery_email: '',
});
const error = ref(null);
const isLoading = ref(false);

const availableRoles = ['admin', 'tesorero', 'comision', 'profesor', 'socio'];

watch(() => props.user, (newUser) => {
  if (newUser) {
    form.value.role = newUser.role;
    form.value.recovery_email = newUser.recovery_email || '';
  }
}, { immediate: true, deep: true });

const handleSubmit = async () => {
  error.value = null;
  isLoading.value = true;
  try {
    const payload = {
      role: form.value.role,
      recovery_email: form.value.recovery_email,
    };
    await apiFetch(`/superadmin/users/${props.user.id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
    emit('user-updated');
    emit('close');
  } catch (e) {
    error.value = e.message;
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Editar Administrador: {{ user.email }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="edit-user-role" class="form-label">Rol</label>
              <select id="edit-user-role" class="form-select" v-model="form.role" required>
                <option v-for="r in availableRoles" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="mb-3">
              <label for="edit-user-recovery" class="form-label">Email de Recuperación</label>
              <input type="email" id="edit-user-recovery" class="form-control" v-model="form.recovery_email" placeholder="correo@real.com" />
              <div class="form-text">El correo "real" donde el usuario recibirá los enlaces para recuperar su contraseña.</div>
            </div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm"></span>
            {{ isLoading ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
