import { ref } from 'vue';

// A reactive state to control the visibility of the session modal
export const isSessionModalVisible = ref(false);

// A reactive state for the message to be displayed in the modal
export const sessionModalMessage = ref('');

// A reactive callback function to be executed when the modal's confirm button is clicked
export const onSessionModalConfirm = ref(() => {});

/**
 * Shows the global session modal with a custom message and a callback for the confirm action.
 * @param {string} message The message to display.
 * @param {function} onConfirm The function to execute when the user clicks "Aceptar".
 */
export function showSessionModal(message, onConfirm) {
  sessionModalMessage.value = message;
  onSessionModalConfirm.value = onConfirm;
  isSessionModalVisible.value = true;
}

/**
 * Hides the global session modal.
 */
export function hideSessionModal() {
  isSessionModalVisible.value = false;
  // Reset callback to avoid accidental execution
  onSessionModalConfirm.value = () => {};
}
