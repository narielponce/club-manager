<script setup>
import { ref, onMounted } from 'vue'
import { currentUser } from '../services/user.js'
import { apiFetch } from '../services/api.js'

const baseFee = ref(0)
const message = ref('')
const error = ref(null)

// When the component mounts, populate the form with the current base_fee
onMounted(() => {
  if (currentUser.value && currentUser.value.club) {
    baseFee.value = currentUser.value.club.base_fee || 0
  }
})

const handleSubmit = async () => {
  error.value = null
  message.value = ''
  try {
    const updatedClub = await apiFetch('/club/settings', {
      method: 'PUT',
      body: JSON.stringify({
        base_fee: parseFloat(baseFee.value)
      }),
    })
    // Update the local state to match
    baseFee.value = updatedClub.base_fee
    // Also update the global state so it's reflected elsewhere
    if (currentUser.value) {
      currentUser.value.club = updatedClub
    }
    message.value = 'Cuota social actualizada con éxito!'
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div>
    <h1>Configuración del Club</h1>
    <div class="card shadow-sm mt-4">
      <div class="card-header">
        <h3>Cuota Social Base</h3>
      </div>
      <div class="card-body">
        <p class="text-muted">Este es el monto base que se le cobrará a cada socio mensualmente al generar la deuda.</p>
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="base_fee" class="form-label">Monto de la Cuota Social</label>
            <div class="input-group" style="max-width: 250px;">
              <span class="input-group-text">$</span>
              <input type="number" step="0.01" id="base_fee" class="form-control" v-model="baseFee" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Guardar Cambios</button>
        </form>
        <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
        <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
      </div>
    </div>
  </div>
</template>
