<script setup>
import { isSessionModalVisible, sessionModalTitle, sessionModalMessage, onSessionModalConfirm, hideSessionModal } from '../services/session.js';

const handleConfirm = () => {
  // Store the callback before it gets reset
  const callback = onSessionModalConfirm.value;
  
  // Now, hide the modal
  hideSessionModal();

  // Finally, execute the stored callback
  if (typeof callback === 'function') {
    callback();
  }
};
</script>

<template>
  <div class="modal fade" :class="{ 'show': isSessionModalVisible, 'd-block': isSessionModalVisible }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ sessionModalTitle }}</h5>
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
