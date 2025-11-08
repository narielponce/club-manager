<script setup>
import { ref, watch } from 'vue';
import { updateClub } from '../services/superadmin.js';

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
});
const error = ref(null);

// Watch for the club prop to change and update the form
watch(() => props.club, (newClub) => {
  if (newClub) {
    form.value.name = newClub.name;
    form.value.base_fee = newClub.base_fee || 0.0;
  }
}, { immediate: true });

const handleSubmit = async () => {
  error.value = null;
  try {
    await updateClub(props.club.id, {
      name: form.value.name,
      base_fee: parseFloat(form.value.base_fee),
    });
    emit('club-updated');
    emit('close');
  } catch (e) {
    error.value = e.message;
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
              <input type="number" step="0.01" id="edit-club-fee" class="form-control" v-model="form.base_fee" required />
            </div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">Guardar Cambios</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
