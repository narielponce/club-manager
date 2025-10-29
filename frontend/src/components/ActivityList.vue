<script setup>
import { ref, reactive } from 'vue'
import { apiFetch } from '../services/api.js'

defineProps({
  activities: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['activity-deleted', 'activity-updated'])

// --- Delete Logic ---
const handleDelete = async (activityId) => {
  if (!confirm('¿Estás seguro de que quieres eliminar esta actividad?')) {
    return
  }
  try {
    await apiFetch(`/activities/${activityId}`, {
      method: 'DELETE',
    })
    emit('activity-deleted')
  } catch (error) {
    alert('Error al eliminar actividad: ' + error.message)
  }
}

// --- Edit Logic ---
const editingActivityId = ref(null)
const editFormData = reactive({ name: '', monthly_cost: '' })

const startEditing = (activity) => {
  editingActivityId.value = activity.id
  editFormData.name = activity.name
  editFormData.monthly_cost = activity.monthly_cost
}

const cancelEditing = () => {
  editingActivityId.value = null
}

const handleUpdate = async (activityId) => {
  try {
    await apiFetch(`/activities/${activityId}`, {
      method: 'PUT',
      body: JSON.stringify({
        name: editFormData.name,
        monthly_cost: parseFloat(editFormData.monthly_cost)
      }),
    })
    emit('activity-updated')
    editingActivityId.value = null // Exit editing mode
  } catch (error) {
    alert('Error al actualizar actividad: ' + error.message)
  }
}
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-header">
      <h3>Actividades del Club</h3>
    </div>
    <div class="card-body">
      <div class="table-responsive">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th scope="col">Nombre</th>
              <th scope="col">Costo Mensual</th>
              <th scope="col" class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="activity in activities" :key="activity.id">
              <template v-if="editingActivityId !== activity.id">
                <td>{{ activity.name }}</td>
                <td>{{ activity.monthly_cost }}</td>
                <td class="text-end">
                  <button @click="startEditing(activity)" class="btn btn-primary btn-sm me-2">Editar</button>
                  <button @click="handleDelete(activity.id)" class="btn btn-danger btn-sm">Eliminar</button>
                </td>
              </template>
              <template v-else>
                <td>
                  <input type="text" v-model="editFormData.name" class="form-control form-control-sm" />
                </td>
                <td>
                  <input type="number" step="0.01" v-model="editFormData.monthly_cost" class="form-control form-control-sm" />
                </td>
                <td class="text-end">
                  <button @click="handleUpdate(activity.id)" class="btn btn-success btn-sm me-2">Guardar</button>
                  <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
                </td>
              </template>
            </tr>
            <tr v-if="activities.length === 0">
              <td colspan="3" class="text-center text-muted">No hay actividades creadas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
