<script setup>
import { ref } from 'vue'
import { apiFetch } from '../services/api.js'

// Default to the current month in YYYY-MM format
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const message = ref('')
const error = ref(null)
const isLoading = ref(false)

const handleSubmit = async () => {
  error.value = null
  message.value = ''
  isLoading.value = true
  try {
    const response = await apiFetch('/generate-monthly-debt', {
      method: 'POST',
      body: JSON.stringify({
        month: selectedMonth.value
      }),
    })
    message.value = response.message
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div>
    <h1>Generación de Deuda Mensual</h1>
    <div class="card shadow-sm mt-4">
      <div class="card-header">
        <h3>Generar Deudas</h3>
      </div>
      <div class="card-body">
        <p class="text-muted">
          Selecciona un mes y haz clic en "Generar" para calcular y registrar la deuda de todos los socios activos.
          Esto incluirá la cuota social y el costo de las actividades en las que estén inscritos.
          El proceso no generará deudas para un socio si ya existe una deuda para ese mes.
        </p>
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="debt-month" class="form-label">Mes a Generar (AAAA-MM)</label>
            <input 
              type="month" 
              id="debt-month" 
              class="form-control" 
              v-model="selectedMonth" 
              required
              style="max-width: 250px;"
            >
          </div>
          <button type="submit" class="btn btn-primary" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ isLoading ? 'Generando...' : 'Generar Deuda' }}
          </button>
        </form>
        <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
        <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
      </div>
    </div>
  </div>
</template>
