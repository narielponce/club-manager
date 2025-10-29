<script setup>
import { reactive, ref } from 'vue'
import { apiFetch } from '../services/api.js'

const emit = defineEmits(['activity-added'])

const newActivity = reactive({
  name: '',
  monthly_cost: ''
})
const message = ref('')
const error = ref(null)

const handleSubmit = async () => {
  error.value = null
  message.value = ''
  try {
    await apiFetch('/activities/', {
      method: 'POST',
      body: JSON.stringify({
        name: newActivity.name,
        monthly_cost: parseFloat(newActivity.monthly_cost)
      }),
    })
    message.value = 'Actividad creada con éxito!'
    newActivity.name = ''
    newActivity.monthly_cost = ''
    emit('activity-added')
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header">
      <h3>Crear Nueva Actividad</h3>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleSubmit">
        <div class="row align-items-end">
          <div class="col-md-8 mb-3">
            <label for="activity-name" class="form-label">Nombre de la Actividad</label>
            <input type="text" id="activity-name" class="form-control" v-model="newActivity.name" required />
          </div>
          <div class="col-md-4 mb-3">
            <label for="activity-cost" class="form-label">Costo Mensual</label>
            <input type="number" step="0.01" id="activity-cost" class="form-control" v-model="newActivity.monthly_cost" required placeholder="0.00" />
          </div>
        </div>
        <button type="submit" class="btn btn-success">Crear Actividad</button>
      </form>
      <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
      <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
    </div>
  </div>
</template>
