<script setup>
import { ref, watch } from 'vue';
import { updateClub, uploadClubLogo } from '../services/superadmin.js';

const props = defineProps({
  show: Boolean,
  club: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close', 'club-updated']);

const form = ref({
  name: '',
  base_fee: 0.0,
  email_domain: '',
});
const logoFile = ref(null);
const error = ref(null);
const isLoading = ref(false);

// Watch for the club prop to change and update the form
watch(() => props.club, (newClub) => {
  if (newClub) {
    form.value.name = newClub.name;
    form.value.base_fee = newClub.base_fee || 0.0;
    form.value.email_domain = newClub.email_domain || '';
    // Do not set logo_url in the form, it's handled separately
  }
}, { immediate: true, deep: true });

const handleFileChange = (event) => {
  logoFile.value = event.target.files[0];
};

const handleSubmit = async () => {
  error.value = null;
  isLoading.value = true;
  try {
    // 1. Update text-based data
    const payload = {
      name: form.value.name,
      base_fee: parseFloat(form.value.base_fee) || 0,
      email_domain: form.value.email_domain,
    };
    await updateClub(props.club.id, payload);

    // 2. If there's a new logo, upload it
    if (logoFile.value) {
      await uploadClubLogo(props.club.id, logoFile.value);
    }

    emit('club-updated');
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
          <h5 class="modal-title">Editar Club: {{ club.name }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="edit-club-name" class="form-label">Nombre del Club</label>
              <input type="text" id="edit-club-name" class="form-control" v-model="form.name" required />
            </div>
            <div class="mb-3">
              <label for="edit-club-fee" class="form-label">Cuota Base</label>
              <input type="number" step="0.01" id="edit-club-fee" class="form-control" v-model="form.base_fee" />
            </div>
            <div class="mb-3">
              <label for="edit-club-domain" class="form-label">Dominio de Correo</label>
              <input type="text" id="edit-club-domain" class="form-control" v-model="form.email_domain" placeholder="ej: mi-club.com" />
               <div class="form-text">Usado para la creación de usuarios dentro del club.</div>
            </div>
            <div class="mb-3">
                <label class="form-label">Logo Actual</label>
                <div>
                    <img v-if="club.logo_url" :src="`/${club.logo_url}`" alt="Logo actual" class="img-thumbnail mb-2" style="max-width: 100px; max-height: 100px;">
                    <p v-else class="text-muted">No hay logo asignado.</p>
                </div>
              <label for="edit-club-logo" class="form-label">Subir Nuevo Logo</label>
              <input type="file" id="edit-club-logo" class="form-control" @change="handleFileChange" accept="image/*" />
            </div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ isLoading ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
