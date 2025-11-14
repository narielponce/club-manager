<script setup>
import { reactive, ref, watch } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'activity-added'])

const newActivity = reactive({
  name: '',
  monthly_cost: ''
})

const message = ref('')
const error = ref(null)

const resetForm = () => {
  newActivity.name = ''
  newActivity.monthly_cost = ''
  message.value = ''
  error.value = null
}

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
    message.value = 'Actividad creada con éxito! Puedes cerrar esta ventana o añadir otra.'
    // Don't reset form fully, just clear the name for quick multi-add
    newActivity.name = '' 
    emit('activity-added')
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        }
      }
// Reset form when modal is closed
watch(() => props.show, (newVal) => {
  if (!newVal) {
    setTimeout(() => {
      resetForm()
    }, 200);
  }
})
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Crear Nueva Actividad</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="modal-activity-name" class="form-label">Nombre de la Actividad</label>
              <input type="text" id="modal-activity-name" class="form-control" v-model="newActivity.name" required />
            </div>
            <div class="mb-3">
              <label for="modal-activity-cost" class="form-label">Costo Mensual</label>
              <input type="number" step="0.01" id="modal-activity-cost" class="form-control" v-model="newActivity.monthly_cost" required placeholder="0.00" />
            </div>
            <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">Guardar Actividad</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
