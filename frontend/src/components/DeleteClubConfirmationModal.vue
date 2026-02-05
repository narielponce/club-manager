<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  clubName: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['close', 'confirm-delete']);

const confirmationText = ref('');

const isConfirmationMatching = computed(() => {
  return confirmationText.value === props.clubName;
});

const handleConfirm = () => {
  if (isConfirmationMatching.value) {
    emit('confirm-delete');
  }
};
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title text-danger">Eliminar Club Permanentemente</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <p>
            Estás a punto de eliminar permanentemente el club
            <strong class="text-danger">{{ clubName }}</strong>.
          </p>
          <p>
            Esta acción es <strong>irreversible</strong> y borrará toda la información asociada, incluyendo:
            <ul>
              <li>Usuarios</li>
              <li>Socios</li>
              <li>Actividades</li>
              <li>Finanzas (deudas, pagos, transacciones)</li>
            </ul>
          </p>
          <p>
            Para confirmar, por favor escribe el nombre del club en el campo de abajo:
            <br>
            <code>{{ clubName }}</code>
          </p>
          <div class="mb-3">
            <input
              type="text"
              class="form-control"
              v-model="confirmationText"
              placeholder="Escribe el nombre del club aquí"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
          <button
            type="button"
            class="btn btn-danger"
            @click="handleConfirm"
            :disabled="!isConfirmationMatching"
          >
            Eliminar Permanentemente
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
