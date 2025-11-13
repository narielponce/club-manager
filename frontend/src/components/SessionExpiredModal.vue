<script setup>
import { isSessionModalVisible, sessionModalMessage, onSessionModalConfirm, hideSessionModal } from '../services/session.js';

const handleConfirm = () => {
  // First, hide the modal
  hideSessionModal();
  // Then, execute the callback (e.g., redirect to login)
  if (typeof onSessionModalConfirm.value === 'function') {
    onSessionModalConfirm.value();
  }
};
</script>

<template>
  <div class="modal fade" :class="{ 'show': isSessionModalVisible, 'd-block': isSessionModalVisible }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Fin de Sesión</h5>
        </div>
        <div class="modal-body">
          <p>{{ sessionModalMessage }}</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click="handleConfirm">Aceptar</button>
        </div>
      </div>
    </div>
  </div>
  <!-- Add backdrop -->
  <div v-if="isSessionModalVisible" class="modal-backdrop fade show"></div>
</template>
