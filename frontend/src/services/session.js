import { ref } from 'vue';

// A reactive state to control the visibility of the session modal
export const isSessionModalVisible = ref(false);

// A reactive state for the title and message to be displayed in the modal
export const sessionModalTitle = ref('');
export const sessionModalMessage = ref('');

// A reactive callback function to be executed when the modal's confirm button is clicked
export const onSessionModalConfirm = ref(() => {});

/**
 * Shows the global session modal with a custom title, message, and a callback for the confirm action.
 * @param {string} title The title for the modal header.
 * @param {string} message The message to display.
 * @param {function} onConfirm The function to execute when the user clicks "Aceptar".
 */
export function showSessionModal(title, message, onConfirm) {
  sessionModalTitle.value = title;
  sessionModalMessage.value = message;
  onSessionModalConfirm.value = onConfirm;
  isSessionModalVisible.value = true;
}

/**
 * Hides the global session modal.
 */
export function hideSessionModal() {
  isSessionModalVisible.value = false;
  // Reset callback and texts to avoid stale data
  onSessionModalConfirm.value = () => {};
  sessionModalTitle.value = '';
  sessionModalMessage.value = '';
}
