<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { apiFetch } from '../services/api.js'
import { useTerminology } from '../composables/useTerminology.js'

const props = defineProps({
  show: Boolean,
  activity: Object,
})

const emit = defineEmits(['close'])

const { t } = useTerminology()

const activeTab = ref('register') // 'register' or 'history'
const enrolledStudents = ref([])
const classRecords = ref([])

const formLoading = ref(false)
const dataLoading = ref(false)
const error = ref(null)

// Form fields
const selectedMemberId = ref('')
const classDate = ref(new Date().toISOString().split('T')[0])
const classHours = ref(1.0)
const classNotes = ref('')

const fetchEnrolledStudents = async () => {
  if (!props.activity) return
  try {
    error.value = null
    const response = await apiFetch(`/members?activity_id=${props.activity.id}&size=1000`)
    enrolledStudents.value = response.items || []
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = 'Error al cargar alumnos: ' + e.message
    }
  }
}

const fetchClassRecords = async () => {
  if (!props.activity) return
  try {
    dataLoading.value = true
    error.value = null
    const response = await apiFetch(`/activities/${props.activity.id}/records`)
    classRecords.value = response.sort((a, b) => new Date(b.date) - new Date(a.date))
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = 'Error al cargar historial: ' + e.message
    }
  } finally {
    dataLoading.value = false
  }
}

const handleSubmitClassRecord = async () => {
  if (!selectedMemberId.value) {
    alert('Por favor selecciona un alumno.')
    return
  }
  if (!classHours.value || classHours.value <= 0) {
    alert('Por favor introduce una cantidad de horas válida.')
    return
  }
  
  try {
    formLoading.value = true
    error.value = null
    
    const payload = {
      member_id: parseInt(selectedMemberId.value),
      activity_id: props.activity.id,
      date: classDate.value,
      hours: parseFloat(classHours.value),
      notes: classNotes.value || null
    }
    
    await apiFetch(`/activities/${props.activity.id}/records`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    
    classNotes.value = ''
    classHours.value = 1.0
    activeTab.value = 'history'
    await fetchClassRecords()
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = 'Error al registrar la clase: ' + e.message
    }
  } finally {
    formLoading.value = false
  }
}

const handleDeleteRecord = async (recordId) => {
  if (!confirm('¿Estás seguro de que quieres eliminar este registro de clase? Esto podría afectar la facturación mensual del alumno.')) {
    return
  }
  
  try {
    dataLoading.value = true
    error.value = null
    await apiFetch(`/activities/records/${recordId}`, {
      method: 'DELETE'
    })
    await fetchClassRecords()
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = 'Error al eliminar el registro: ' + e.message
    }
  } finally {
    dataLoading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    activeTab.value = 'register'
    selectedMemberId.value = ''
    classNotes.value = ''
    classHours.value = 1.0
    classDate.value = new Date().toISOString().split('T')[0]
    fetchEnrolledStudents()
    fetchClassRecords()
  }
}, { immediate: true })

onMounted(() => {
  if (props.show) {
    fetchEnrolledStudents()
    fetchClassRecords()
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const [year, month, day] = dateStr.split('-')
  return `${day}/${month}/${year}`
}
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable" role="document">
      <div class="modal-content shadow border-0 rounded-3">
        
        <!-- Modal Header -->
        <div class="modal-header bg-dark text-white border-0 py-2">
          <div class="d-flex align-items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-clock-history me-2 text-info" viewBox="0 0 16 16">
              <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022zm2.004.45a7 7 0 0 0-.985-.299l.219-.976c.383.086.76.2 1.126.342zm1.37.71a7 7 0 0 0-.439-.74l.824-.569c.192.278.364.57.514.874zm1.205 1.12a7 7 0 0 0-.66-.464l.57-.824c.285.197.548.423.788.675zm.74 1.37a7 7 0 0 0-.342-1.126l.976-.219c.15.385.267.77.35 1.163zM16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M4.5 9a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1z"/>
            </svg>
            <h6 class="modal-title fw-semibold m-0 fs-6">Clases dictadas: <span class="text-info">{{ activity?.name }}</span></h6>
          </div>
          <button type="button" class="btn-close btn-close-white" @click="$emit('close')" aria-label="Close"></button>
        </div>

        <!-- Tabs Navigation -->
        <div class="bg-light px-3 pt-2 border-bottom">
          <ul class="nav nav-tabs border-0 small">
            <li class="nav-item">
              <button 
                class="nav-link border-0 text-dark py-1.5 px-3 fw-semibold small" 
                :class="{ 'active bg-white border-bottom-0 rounded-top': activeTab === 'register' }"
                @click="activeTab = 'register'"
              >
                Registrar Clase
              </button>
            </li>
            <li class="nav-item">
              <button 
                class="nav-link border-0 text-dark py-1.5 px-3 fw-semibold small" 
                :class="{ 'active bg-white border-bottom-0 rounded-top': activeTab === 'history' }"
                @click="activeTab = 'history'"
              >
                Historial de Clases
                <span v-if="classRecords.length > 0" class="badge bg-secondary ms-1 small" style="font-size: 0.75rem;">{{ classRecords.length }}</span>
              </button>
            </li>
          </ul>
        </div>

        <!-- Modal Body -->
        <div class="modal-body p-3 bg-white">
          <div v-if="error" class="alert alert-danger d-flex align-items-center mb-3 py-2 px-3 small" role="alert">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle-fill me-2" viewBox="0 0 16 16">
              <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2"/>
            </svg>
            <div>{{ error }}</div>
          </div>

          <!-- TAB: REGISTER -->
          <div v-if="activeTab === 'register'" class="tab-pane-content fade show active">
            <div v-if="enrolledStudents.length === 0" class="text-center py-3">
              <div class="alert alert-warning d-inline-block px-3 py-2 small mb-0">
                No hay alumnos inscriptos en esta actividad para registrar clases.
              </div>
            </div>

            <form v-else @submit.prevent="handleSubmitClassRecord" class="small">
              <div class="mb-2">
                <label for="studentSelect" class="form-label fw-semibold mb-1 text-muted small">Alumno <span class="text-danger">*</span></label>
                <select 
                  id="studentSelect" 
                  class="form-select form-select-sm border rounded-2" 
                  v-model="selectedMemberId" 
                  required
                >
                  <option value="" disabled>Selecciona un alumno...</option>
                  <option v-for="student in enrolledStudents" :key="student.id" :value="student.id">
                    {{ student.last_name }}, {{ student.first_name }} (DNI: {{ student.dni || 'N/A' }})
                  </option>
                </select>
              </div>

              <div class="row g-2 mb-2">
                <div class="col-md-6">
                  <label for="classDate" class="form-label fw-semibold mb-1 text-muted small">Fecha <span class="text-danger">*</span></label>
                  <input 
                    type="date" 
                    id="classDate" 
                    class="form-control form-control-sm border rounded-2" 
                    v-model="classDate" 
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label for="classHours" class="form-label fw-semibold mb-1 text-muted small">Cantidad de Horas / Sesiones <span class="text-danger">*</span></label>
                  <input 
                    type="number" 
                    id="classHours" 
                    class="form-control form-control-sm border rounded-2" 
                    step="0.1" 
                    min="0.1" 
                    v-model="classHours" 
                    required
                  >
                </div>
              </div>

              <div class="mb-3">
                <label for="classNotes" class="form-label fw-semibold mb-1 text-muted small">Notas / Comentarios (opcional)</label>
                <textarea 
                  id="classNotes" 
                  class="form-control form-control-sm border rounded-2" 
                  rows="2" 
                  v-model="classNotes" 
                  placeholder="Temas tratados, progreso, notas..."
                ></textarea>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary btn-sm px-3" @click="$emit('close')">Cancelar</button>
                <button type="submit" class="btn btn-primary btn-sm px-4" :disabled="formLoading">
                  <span v-if="formLoading" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  Guardar Clase
                </button>
              </div>
            </form>
          </div>

          <!-- TAB: HISTORY -->
          <div v-if="activeTab === 'history'" class="tab-pane-content fade show active">
            <div v-if="dataLoading" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
              </div>
            </div>

            <div v-else-if="classRecords.length === 0" class="text-center py-4 text-muted small">
              <p class="m-0">No hay clases registradas para esta actividad.</p>
            </div>

            <div v-else class="table-responsive" style="max-height: 300px;">
              <table class="table table-striped table-hover align-middle table-sm border-top small" style="font-size: 0.85rem;">
                <thead class="table-dark">
                  <tr>
                    <th scope="col" style="width: 100px;">Fecha</th>
                    <th scope="col">Alumno</th>
                    <th scope="col" class="text-center" style="width: 70px;">Horas</th>
                    <th scope="col" class="text-end" style="width: 90px;">Monto</th>
                    <th scope="col">Notas / Temas</th>
                    <th scope="col" class="text-end" style="width: 70px;">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in classRecords" :key="record.id">
                    <td class="text-secondary small">{{ formatDate(record.date) }}</td>
                    <td>
                      <div class="fw-semibold text-dark">{{ record.member?.last_name }}, {{ record.member?.first_name }}</div>
                      <small class="text-muted" style="font-size: 0.75rem;" v-if="record.member?.dni">DNI: {{ record.member?.dni }}</small>
                    </td>
                    <td class="text-center fw-semibold">{{ record.hours }}</td>
                    <td class="text-end fw-semibold text-success">{{ $formatCurrency(record.amount) }}</td>
                    <td>
                      <span v-if="record.notes" class="text-wrap text-secondary" style="font-size: 0.8rem;">{{ record.notes }}</span>
                      <span v-else class="text-muted italic small" style="font-size: 0.75rem;">-</span>
                    </td>
                    <td class="text-end">
                      <button 
                        class="btn btn-link text-danger btn-sm p-0 border-0"
                        title="Eliminar registro" 
                        @click="handleDeleteRecord(record.id)"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                          <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"/>
                        </svg>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer border-0 bg-light py-2">
          <button type="button" class="btn btn-secondary btn-sm px-3" @click="$emit('close')">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<style scoped>
.modal-backdrop {
  z-index: 1040;
}
.modal {
  z-index: 1050;
  background-color: rgba(0, 0, 0, 0.4);
}
.nav-link {
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent !important;
  font-size: 0.85rem;
}
.nav-link.active {
  border-bottom: 2px solid #0dcaf0 !important;
  color: #0dcaf0 !important;
}
.italic {
  font-style: italic;
}
.text-wrap {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
