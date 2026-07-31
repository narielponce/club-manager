<script setup>
import { ref, reactive, computed } from 'vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'
import { useTerminology } from '../composables/useTerminology.js'
import ActivityRecordsModal from './ActivityRecordsModal.vue'

defineProps({
  activities: {
    type: Array,
    required: true
  },
  professors: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['activity-deleted', 'activity-updated'])
const { t } = useTerminology()

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const currentUserId = computed(() => currentUser.value?.id)

const selectedActivityForRecords = ref(null)
const isRecordsModalVisible = ref(false)

const openRecordsModal = (activity) => {
  selectedActivityForRecords.value = activity
  isRecordsModalVisible.value = true
}

// --- Delete Logic ---
const handleDelete = async (activityId) => {
  if (!confirm(`¿Estás seguro de que quieres eliminar esta ${t('activity').toLowerCase()}?`)) {
    return
  }
  try {
    await apiFetch(`/activities/${activityId}`, {
      method: 'DELETE',
    })
    emit('activity-deleted')
  } catch (error) {
    if (error.name !== "SessionExpiredError") {
      alert('Error al eliminar: ' + error.message)
    }
  }
}

// --- Edit Logic ---
const editingActivityId = ref(null)
const editFormData = reactive({ name: '', monthly_cost: '', profesor_id: null, billing_type: 'monthly' })

const startEditing = (activity) => {
  editingActivityId.value = activity.id
  editFormData.name = activity.name
  editFormData.monthly_cost = activity.monthly_cost
  editFormData.profesor_id = activity.profesor?.id || null
  editFormData.billing_type = activity.billing_type || 'monthly'
}

const cancelEditing = () => {
  editingActivityId.value = null
}

const handleUpdate = async (activityId) => {
  try {
    const payload = {
      name: editFormData.name,
      monthly_cost: parseFloat(editFormData.monthly_cost),
      profesor_id: editFormData.profesor_id || null,
      billing_type: editFormData.billing_type
    };
    await apiFetch(`/activities/${activityId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    emit('activity-updated')
    editingActivityId.value = null // Exit editing mode
  } catch (error) {
    if (error.name !== "SessionExpiredError") {
      alert('Error al actualizar: ' + error.message)
    }
  }
}
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-header">
      <h3>{{ t('activities') }} de la {{ t('organization') }}</h3>
    </div>
    <div class="card-body">
      <!-- Desktop view: Table -->
      <div class="table-responsive d-none d-lg-block">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th scope="col">Nombre</th>
              <th scope="col">Tipo de Cobro</th>
              <th scope="col">Costo</th>
              <th scope="col">{{ t('professor') }} Asignado</th>
              <th scope="col" class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="activity in activities" :key="activity.id">
              <template v-if="editingActivityId !== activity.id">
                <td>{{ activity.name }}</td>
                <td>
                  <span class="badge" :class="activity.billing_type === 'per_class' ? 'bg-info text-dark' : 'bg-secondary'">
                    {{ activity.billing_type === 'per_class' ? 'Por Clase / Sesión' : 'Mensual Fijo' }}
                  </span>
                </td>
                <td>{{ $formatCurrency(activity.monthly_cost) }}</td>
                <td>{{ activity.profesor?.email || 'Sin asignar' }}</td>
                <td class="text-end">
                  <button v-if="activity.billing_type === 'per_class' && (isAdmin || activity.profesor?.id === currentUserId)" 
                          @click="openRecordsModal(activity)" 
                          class="btn btn-info btn-sm me-2">
                    Registrar Clases
                  </button>
                  <button v-if="isAdmin" @click="startEditing(activity)" class="btn btn-primary btn-sm me-2">Editar</button>
                  <button v-if="isAdmin" @click="handleDelete(activity.id)" class="btn btn-danger btn-sm">Eliminar</button>
                </td>
              </template>
              <template v-else>
                <td>
                  <input type="text" v-model="editFormData.name" class="form-control form-control-sm" />
                </td>
                <td>
                  <select class="form-select form-select-sm" v-model="editFormData.billing_type">
                    <option value="monthly">Mensual Fijo</option>
                    <option value="per_class">Por Clase / Sesión</option>
                  </select>
                </td>
                <td>
                  <input type="number" step="0.01" v-model="editFormData.monthly_cost"
                    class="form-control form-control-sm" />
                </td>
                <td>
                  <select class="form-select form-select-sm" v-model="editFormData.profesor_id">
                    <option :value="null">Sin asignar</option>
                    <option v-for="profesor in professors" :key="profesor.id" :value="profesor.id">
                      {{ profesor.email }}
                    </option>
                  </select>
                </td>
                <td class="text-end">
                  <button @click="handleUpdate(activity.id)" class="btn btn-success btn-sm me-2">Guardar</button>
                  <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
                </td>
              </template>
            </tr>
            <tr v-if="activities.length === 0">
              <td colspan="5" class="text-center text-muted">No hay {{ t('activities').toLowerCase() }} creadas.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile view: Cards -->
      <div class="d-block d-lg-none">
        <div v-if="activities.length === 0" class="text-center text-muted">
          No hay {{ t('activities').toLowerCase() }} creadas.
        </div>
        <div v-for="activity in activities" :key="`mobile-${activity.id}`" class="card mb-3">
          <!-- View Mode -->
          <template v-if="editingActivityId !== activity.id">
            <div class="card-body">
              <h5 class="card-title">{{ activity.name }}</h5>
              <p class="card-text mb-1">
                <strong>Tipo de Cobro:</strong> {{ activity.billing_type === 'per_class' ? 'Por Clase / Sesión' : 'Mensual Fijo' }}
              </p>
              <p class="card-text mb-1">
                <strong>Costo:</strong> {{ $formatCurrency(activity.monthly_cost) }}
              </p>
              <p class="card-text text-muted">
                <strong>{{ t('professor') }}:</strong> {{ activity.profesor?.email || 'Sin asignar' }}
              </p>
            </div>
            <div class="card-footer bg-transparent d-flex justify-content-end gap-2 flex-wrap">
              <button v-if="activity.billing_type === 'per_class' && (isAdmin || activity.profesor?.id === currentUserId)" 
                      @click="openRecordsModal(activity)" 
                      class="btn btn-info btn-sm">
                Registrar Clases
              </button>
              <button v-if="isAdmin" @click="startEditing(activity)" class="btn btn-primary btn-sm">Editar</button>
              <button v-if="isAdmin" @click="handleDelete(activity.id)" class="btn btn-danger btn-sm">Eliminar</button>
            </div>
          </template>
          <!-- Edit Mode -->
          <template v-else>
            <div class="card-body">
              <h5 class="card-title">Editando {{ t('activity') }}</h5>
              <div class="mb-2">
                <label class="form-label">Nombre</label>
                <input type="text" v-model="editFormData.name" class="form-control form-control-sm" />
              </div>
              <div class="mb-2">
                <label class="form-label">Tipo de Cobro</label>
                <select class="form-select form-select-sm" v-model="editFormData.billing_type">
                  <option value="monthly">Mensual Fijo</option>
                  <option value="per_class">Por Clase / Sesión</option>
                </select>
              </div>
              <div class="mb-2">
                <label class="form-label">
                  {{ editFormData.billing_type === 'per_class' ? 'Costo por Clase' : 'Costo Mensual' }}
                </label>
                <input type="number" step="0.01" v-model="editFormData.monthly_cost" class="form-control form-control-sm" />
              </div>
              <div class="mb-2">
                <label class="form-label">{{ t('professor') }}</label>
                <select class="form-select form-select-sm" v-model="editFormData.profesor_id">
                  <option :value="null">Sin asignar</option>
                  <option v-for="profesor in professors" :key="profesor.id" :value="profesor.id">
                    {{ profesor.email }}
                  </option>
                </select>
              </div>
            </div>
            <div class="card-footer bg-transparent d-flex justify-content-end gap-2">
              <button @click="handleUpdate(activity.id)" class="btn btn-success btn-sm">Guardar</button>
              <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- Activity Records Modal (Register classes & History) -->
    <ActivityRecordsModal
      v-if="isRecordsModalVisible"
      :show="isRecordsModalVisible"
      :activity="selectedActivityForRecords"
      @close="isRecordsModalVisible = false"
    />
  </div>
</template>
