<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Agenda y Horarios</h1>
      <div class="d-flex gap-2">
        <button v-if="isFinanceAdmin" class="btn btn-outline-secondary" @click="openSpacesModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-geo-alt-fill me-1" viewBox="0 0 16 16">
            <path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z"/>
          </svg>
          Gestionar Espacios
        </button>
        <button class="btn btn-primary" @click="openAddScheduleModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-calendar-plus me-1" viewBox="0 0 16 16">
            <path d="M8 7a.5.5 0 0 1 .5.5V9H10a.5.5 0 0 1 0 1H8.5v1.5a.5.5 0 0 1-1 0V10H6a.5.5 0 0 1 0-1h1.5V7.5A.5.5 0 0 1 8 7z"/>
            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
          </svg>
          Reservar Horario
        </button>
      </div>
    </div>

    <!-- Error/Loading Notifications -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Main Filters card -->
    <div class="card mb-4 border-0 shadow-sm">
      <div class="card-body">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label for="filter-mode" class="form-label fw-bold">Visualizar por:</label>
            <select id="filter-mode" class="form-select" v-model="filterMode">
              <option value="space">Espacio Físico (Canchas / Aulas)</option>
              <option value="professor">{{ t('professor') }} / Tutor</option>
            </select>
          </div>

          <div class="col-md-4" v-if="filterMode === 'space'">
            <label for="filter-space" class="form-label fw-bold">Seleccionar Espacio:</label>
            <select id="filter-space" class="form-select" v-model="selectedSpaceId">
              <option :value="null">-- Todos los Espacios --</option>
              <option v-for="space in spaces" :key="space.id" :value="space.id">
                {{ space.name }}
              </option>
            </select>
          </div>

          <div class="col-md-4" v-if="filterMode === 'professor'">
            <label for="filter-prof" class="form-label fw-bold">Seleccionar {{ t('professor') }}:</label>
            <select id="filter-prof" class="form-select" v-model="selectedProfessorId" :disabled="isProfessor">
              <option :value="null" v-if="!isProfessor">-- Todos los {{ t('professors') }} --</option>
              <option v-for="prof in professors" :key="prof.id" :value="prof.id">
                {{ prof.email }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Weekly grid container -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando agenda...</span>
      </div>
    </div>

    <div v-else class="weekly-grid-container table-responsive">
      <div class="d-flex gap-3 pb-3" style="min-width: 900px;">
        <div v-for="day in daysOfWeek" :key="day.value" class="day-column flex-fill bg-white rounded-3 shadow-sm p-3">
          <div class="day-header text-center pb-2 mb-3 border-bottom">
            <h5 class="m-0 fw-bold text-primary">{{ day.name }}</h5>
          </div>
          <div class="day-cards d-flex flex-column gap-2">
            <div 
              v-for="sched in getSchedulesForDay(day.value)" 
              :key="sched.id" 
              class="schedule-card p-3 rounded border"
              :class="getCardClass(sched)"
            >
              <div class="d-flex justify-content-between align-items-start">
                <span class="fw-bold fs-6 text-truncate" style="max-width: 140px;" :title="sched.activity.name">
                  {{ sched.activity.name }}
                </span>
                <button 
                  v-if="canDeleteSchedule(sched)"
                  @click="deleteSchedule(sched.id)" 
                  class="btn btn-link text-danger p-0 border-0" 
                  title="Eliminar horario"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-trash3-fill" viewBox="0 0 16 16">
                    <path d="M11 1.5v1h3.5a.5.5 0 0 1 0 1h-.538l-.853 10.66A2 2 0 0 1 11.115 16h-6.23a2 2 0 0 1-1.994-1.84L2.038 3.5H1.5a.5.5 0 0 1 0-1H5v-1A1.5 1.5 0 0 1 6.5 0h3A1.5 1.5 0 0 1 11 1.5Zm-5 0v1h4v-1a.5.5 0 0 0-.5-.5h-3a.5.5 0 0 0-.5.5ZM4.5 5.029l.5 8.5a.5.5 0 1 0 .998-.06l-.5-8.5a.5.5 0 1 0-.998.06Zm6.53-.528a.5.5 0 0 0-.528.47l-.5 8.5a.5.5 0 0 0 .998.058l.5-8.5a.5.5 0 0 0-.47-.528ZM8 4.5a.5.5 0 0 0-.5.5v8.5a.5.5 0 0 0 1 0V5a.5.5 0 0 0-.5-.5Z"/>
                  </svg>
                </button>
              </div>
              <div class="mt-2 text-muted small">
                <div class="d-flex align-items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16">
                    <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                    <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                  </svg>
                  <span>{{ formatTime(sched.start_time) }} - {{ formatTime(sched.end_time) }}</span>
                </div>
                <div class="d-flex align-items-center gap-1 mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-geo-alt" viewBox="0 0 16 16">
                    <path d="M12.166 8.94c-.524 1.062-1.234 2.12-1.96 3.07A31.493 31.493 0 0 1 8 14.58a31.481 31.481 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304 7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94zM8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10z"/>
                    <path d="M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                  </svg>
                  <span class="text-truncate" style="max-width: 130px;">{{ sched.space.name }}</span>
                </div>
                <div class="d-flex align-items-center gap-1 mt-1" v-if="filterMode !== 'professor' && sched.activity.profesor">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-person" viewBox="0 0 16 16">
                    <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
                  </svg>
                  <span class="text-truncate" style="max-width: 130px;" :title="sched.activity.profesor.email">{{ sched.activity.profesor.email.split('@')[0] }}</span>
                </div>

                <!-- Alumnos inscriptos -->
                <div v-if="sched.activity.members && sched.activity.members.length > 0" class="mt-2 pt-2 border-top border-black-25">
                  <div class="fw-bold mb-1" style="font-size: 0.75rem;">{{ t('members') }}:</div>
                  <div v-for="member in sched.activity.members" :key="member.id" class="d-flex align-items-center gap-1 mt-1 text-dark" style="font-size: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">
                      <path d="M3 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H3zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                    </svg>
                    <span class="text-truncate" style="max-width: 130px;" :title="`${member.first_name} ${member.last_name}`">
                      {{ member.first_name }} {{ member.last_name }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="getSchedulesForDay(day.value).length === 0" class="text-center py-4 text-muted small border border-dashed rounded-3">
              Sin clases
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Space Management Modal -->
    <div class="modal fade" :class="{ 'show': isSpacesModalOpen, 'd-block': isSpacesModalOpen }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-md modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Gestión de Espacios Físicos</h5>
            <button type="button" class="btn-close" @click="isSpacesModalOpen = false"></button>
          </div>
          <div class="modal-body">
            <!-- Add Space Form -->
            <form @submit.prevent="createSpace" class="mb-4 bg-light p-3 rounded">
              <h6 class="fw-bold mb-3">Nuevo Espacio</h6>
              <div class="row g-2">
                <div class="col-12">
                  <input type="text" class="form-control form-control-sm" v-model="newSpaceName" placeholder="Nombre (ej. Cancha 1, Aula 101)" required />
                </div>
                <div class="col-8">
                  <input type="text" class="form-control form-control-sm" v-model="newSpaceDesc" placeholder="Descripción (opcional)" />
                </div>
                <div class="col-4">
                  <input type="number" class="form-control form-control-sm" v-model="newSpaceCapacity" placeholder="Capac." min="0" />
                </div>
                <div class="col-12 text-end mt-2">
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="isCreatingSpace">Agregar</button>
                </div>
              </div>
            </form>

            <!-- List Spaces -->
            <h6 class="fw-bold mb-2">Espacios Existentes</h6>
            <div class="list-group list-group-flush border rounded overflow-auto" style="max-height: 250px;">
              <div v-for="space in spaces" :key="space.id" class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <span class="fw-bold">{{ space.name }}</span>
                  <span v-if="space.description" class="text-muted d-block small">{{ space.description }}</span>
                  <span v-if="space.capacity" class="text-secondary small">Capacidad: {{ space.capacity }}</span>
                </div>
                <button @click="deleteSpace(space.id)" class="btn btn-link text-danger p-0 border-0">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash-fill" viewBox="0 0 16 16">
                    <path d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0z"/>
                  </svg>
                </button>
              </div>
              <div v-if="spaces.length === 0" class="p-3 text-center text-muted small">No hay espacios creados.</div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary btn-sm" @click="isSpacesModalOpen = false">Cerrar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Schedule Modal -->
    <div class="modal fade" :class="{ 'show': isAddScheduleModalOpen, 'd-block': isAddScheduleModalOpen }" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-md modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Agendar Horario</h5>
            <button type="button" class="btn-close" @click="isAddScheduleModalOpen = false"></button>
          </div>
          <form @submit.prevent="createSchedule">
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger mb-3">{{ formError }}</div>

              <div class="mb-3">
                <label for="sched-activity" class="form-label fw-bold">Seleccionar {{ t('activity') }}:</label>
                <select id="sched-activity" class="form-select" v-model="formData.activity_id" required>
                  <option :value="null" disabled>-- Elige una {{ t('activity').toLowerCase() }} --</option>
                  <option v-for="act in myActivities" :key="act.id" :value="act.id">
                    {{ act.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="sched-space" class="form-label fw-bold">Espacio Físico:</label>
                <select id="sched-space" class="form-select" v-model="formData.space_id" required>
                  <option :value="null" disabled>-- Elige un espacio físico --</option>
                  <option v-for="space in spaces" :key="space.id" :value="space.id">
                    {{ space.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="sched-day" class="form-label fw-bold">Día de la Semana:</label>
                <select id="sched-day" class="form-select" v-model="formData.day_of_week" required>
                  <option v-for="day in daysOfWeek" :key="day.value" :value="day.value">
                    {{ day.name }}
                  </option>
                </select>
              </div>

              <div class="row">
                <div class="col-6 mb-3">
                  <label for="sched-start" class="form-label fw-bold">Hora de Inicio:</label>
                  <input type="time" id="sched-start" class="form-control" v-model="formData.start_time" required />
                </div>
                <div class="col-6 mb-3">
                  <label for="sched-end" class="form-label fw-bold">Hora de Fin:</label>
                  <input type="time" id="sched-end" class="form-control" v-model="formData.end_time" required />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary btn-sm" @click="isAddScheduleModalOpen = false">Cancelar</button>
              <button type="submit" class="btn btn-primary btn-sm" :disabled="isCreatingSchedule">Guardar Horario</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Backdrop -->
    <div v-if="isSpacesModalOpen || isAddScheduleModalOpen" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'
import { useTerminology } from '../composables/useTerminology.js'

const { t } = useTerminology()

// --- Role Logic ---
const isAdmin = computed(() => currentUser.value?.role === 'admin')
const isFinanceAdmin = computed(() => currentUser.value?.role === 'admin' || currentUser.value?.role === 'tesorero')
const isProfessor = computed(() => currentUser.value?.role === 'profesor')

// --- Filters & State ---
const filterMode = ref('space')
const selectedSpaceId = ref(null)
const selectedProfessorId = ref(null)

const spaces = ref([])
const schedules = ref([])
const professors = ref([])
const myActivities = ref([])

const isLoading = ref(true)
const error = ref(null)

// --- Days of Week definition ---
const daysOfWeek = [
  { value: 0, name: 'Lunes' },
  { value: 1, name: 'Martes' },
  { value: 2, name: 'Miércoles' },
  { value: 3, name: 'Jueves' },
  { value: 4, name: 'Viernes' },
  { value: 5, name: 'Sábado' },
  { value: 6, name: 'Domingo' }
]

// --- Modal management state ---
const isSpacesModalOpen = ref(false)
const isAddScheduleModalOpen = ref(false)

// --- Forms data ---
const newSpaceName = ref('')
const newSpaceDesc = ref('')
const newSpaceCapacity = ref(null)
const isCreatingSpace = ref(false)

const formData = ref({
  activity_id: null,
  space_id: null,
  day_of_week: 0,
  start_time: '14:00',
  end_time: '15:30'
})
const formError = ref(null)
const isCreatingSchedule = ref(false)

// --- Fetch Functions ---
const fetchSpaces = async () => {
  try {
    spaces.value = await apiFetch('/physical-spaces/')
  } catch (e) {
    console.error("Error fetching spaces:", e)
  }
}

const fetchProfessors = async () => {
  try {
    const allUsers = await apiFetch('/users')
    professors.value = allUsers.filter(u => u.role === 'profesor')
  } catch (e) {
    console.error("Error fetching professors:", e)
  }
}

const fetchMyActivities = async () => {
  try {
    const list = await apiFetch('/activities/')
    if (isProfessor.value) {
      myActivities.value = list.filter(act => act.profesor_id === currentUser.value?.id)
    } else {
      myActivities.value = list
    }
  } catch (e) {
    console.error("Error fetching activities:", e)
  }
}

const fetchSchedules = async () => {
  isLoading.value = true
  error.value = null
  try {
    let url = '/schedules/'
    const params = []
    if (filterMode.value === 'space' && selectedSpaceId.value !== null) {
      params.push(`space_id=${selectedSpaceId.value}`)
    }
    if (filterMode.value === 'professor' && selectedProfessorId.value !== null) {
      params.push(`profesor_id=${selectedProfessorId.value}`)
    }
    
    if (params.length > 0) {
      url += '?' + params.join('&')
    }
    
    schedules.value = await apiFetch(url)
  } catch (e) {
    error.value = 'Error al cargar los horarios: ' + e.message
  } finally {
    isLoading.value = false
  }
}

// Watch filters
watch([filterMode, selectedSpaceId, selectedProfessorId], () => {
  fetchSchedules()
})

watch(filterMode, (newVal) => {
  if (newVal === 'space') {
    selectedProfessorId.value = null
  } else {
    selectedSpaceId.value = null
    if (isProfessor.value) {
      selectedProfessorId.value = currentUser.value?.id
    }
  }
})

// --- Init ---
onMounted(async () => {
  if (isProfessor.value) {
    filterMode.value = 'professor'
    selectedProfessorId.value = currentUser.value?.id
  }
  await Promise.all([
    fetchSpaces(),
    fetchMyActivities(),
    fetchProfessors(),
    fetchSchedules()
  ])
})

// --- Helper Functions ---
const getSchedulesForDay = (dayValue) => {
  return schedules.value
    .filter(s => s.day_of_week === dayValue)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  const parts = timeString.split(':')
  return `${parts[0]}:${parts[1]}`
}

const getCardClass = (sched) => {
  // Give distinct colorful border and background to slots based on activity id
  const colors = [
    'border-start border-primary border-4 bg-primary-subtle text-primary-emphasis',
    'border-start border-success border-4 bg-success-subtle text-success-emphasis',
    'border-start border-danger border-4 bg-danger-subtle text-danger-emphasis',
    'border-start border-warning border-4 bg-warning-subtle text-warning-emphasis',
    'border-start border-info border-4 bg-info-subtle text-info-emphasis',
    'border-start border-secondary border-4 bg-secondary-subtle text-secondary-emphasis'
  ]
  return colors[sched.activity_id % colors.length]
}

const canDeleteSchedule = (sched) => {
  if (isAdmin.value || currentUser.value?.role === 'tesorero') return true
  if (isProfessor.value && sched.activity.profesor_id === currentUser.value?.id) return true
  return false
}

// --- Event Handlers ---
const openSpacesModal = () => {
  isSpacesModalOpen.value = true
}

const openAddScheduleModal = () => {
  formError.value = null
  formData.value = {
    activity_id: myActivities.value.length > 0 ? myActivities.value[0].id : null,
    space_id: spaces.value.length > 0 ? spaces.value[0].id : null,
    day_of_week: 0,
    start_time: '14:00',
    end_time: '15:30'
  }
  isAddScheduleModalOpen.value = true
}

const createSpace = async () => {
  isCreatingSpace.value = true
  error.value = null
  try {
    await apiFetch('/physical-spaces/', {
      method: 'POST',
      body: JSON.stringify({
        name: newSpaceName.value,
        description: newSpaceDesc.value || null,
        capacity: newSpaceCapacity.value || 0
      })
    })
    newSpaceName.value = ''
    newSpaceDesc.value = ''
    newSpaceCapacity.value = null
    await fetchSpaces()
  } catch (e) {
    error.value = 'Error al crear espacio: ' + e.message
  } finally {
    isCreatingSpace.value = false
  }
}

const deleteSpace = async (spaceId) => {
  if (!confirm('¿Estás seguro de que deseas eliminar este espacio físico? Esto quitará todos los horarios asociados.')) return
  error.value = null
  try {
    await apiFetch(`/physical-spaces/${spaceId}`, { method: 'DELETE' })
    await Promise.all([fetchSpaces(), fetchSchedules()])
  } catch (e) {
    error.value = 'Error al eliminar espacio: ' + e.message
  }
}

const createSchedule = async () => {
  formError.value = null
  isCreatingSchedule.value = true
  try {
    await apiFetch('/schedules/', {
      method: 'POST',
      body: JSON.stringify({
        activity_id: formData.value.activity_id,
        space_id: formData.value.space_id,
        day_of_week: formData.value.day_of_week,
        start_time: formData.value.start_time + ':00',
        end_time: formData.value.end_time + ':00'
      })
    })
    isAddScheduleModalOpen.value = false
    await fetchSchedules()
  } catch (e) {
    formError.value = e.message
  } finally {
    isCreatingSchedule.value = false
  }
}

const deleteSchedule = async (scheduleId) => {
  if (!confirm('¿Deseas quitar este horario programado?')) return
  error.value = null
  try {
    await apiFetch(`/schedules/${scheduleId}`, { method: 'DELETE' })
    await fetchSchedules()
  } catch (e) {
    error.value = 'Error al eliminar horario: ' + e.message
  }
}
</script>

<style scoped>
.weekly-grid-container {
  overflow-x: auto;
}

.day-column {
  min-width: 170px;
  max-width: 250px;
  border: 1px solid #e3e6f0;
  transition: all 0.2s ease-in-out;
}

.day-column:hover {
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.08) !important;
}

.day-header {
  border-bottom: 2px solid #eaecf4;
}

.schedule-card {
  font-size: 0.85rem;
  transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: default;
}

.schedule-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.06);
}

.border-dashed {
  border-style: dashed !important;
}
</style>
