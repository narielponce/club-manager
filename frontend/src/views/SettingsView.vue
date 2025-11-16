<script setup>
import { ref, onMounted } from 'vue'
import { currentUser } from '../services/user.js'
import { apiFetch } from '../services/api.js'
import CategoryManager from '../components/CategoryManager.vue'

// --- Base Fee Logic ---
const baseFee = ref(0)
const baseFeeMessage = ref('')
const baseFeeError = ref(null)

// --- Lifecycle ---
onMounted(() => {
  if (currentUser.value && currentUser.value.club) {
    baseFee.value = currentUser.value.club.base_fee || 0
  }
})

// --- Methods ---
const handleBaseFeeSubmit = async () => {
  baseFeeError.value = null
  baseFeeMessage.value = ''
  try {
    const updatedClub = await apiFetch('/club/settings', {
      method: 'PUT',
      body: JSON.stringify({
        base_fee: parseFloat(baseFee.value)
      }),
    })
    baseFee.value = updatedClub.base_fee
    if (currentUser.value) {
      currentUser.value.club = updatedClub
    }
    baseFeeMessage.value = 'Cuota social actualizada con éxito!'
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
          baseFeeError.value = e.message
        }
  }
}
</script>

<template>
  <div>
    <h1>Configuración y Tareas</h1>

    <!-- Base Fee Card -->
    <div class="card shadow-sm mt-4">
      <div class="card-header">
        <h3>Cuota Social Base</h3>
      </div>
      <div class="card-body">
        <p class="text-muted">Importe base de cuota societaria que se le cobrará a cada socio mensualmente.</p>
        <form @submit.prevent="handleBaseFeeSubmit">
          <div class="mb-3">
            <label for="base_fee" class="form-label">Monto de la Cuota Social</label>
            <div class="input-group" style="max-width: 250px;">
              <span class="input-group-text">$</span>
              <input type="number" step="1" id="base_fee" class="form-control" v-model="baseFee" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Guardar Cambios</button>
        </form>
        <div v-if="baseFeeMessage" class="alert alert-success mt-3 py-2">{{ baseFeeMessage }}</div>
        <div v-if="baseFeeError" class="alert alert-danger mt-3 py-2">{{ baseFeeError }}</div>
      </div>
    </div>

    <!-- Category Manager Component -->
    <CategoryManager />

  </div>
</template>
