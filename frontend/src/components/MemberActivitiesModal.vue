<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
  member: Object,
})

const emit = defineEmits(['close', 'update:member'])

const allActivities = ref([])
const error = ref(null)
const isLoading = ref(false)

const memberActivityIds = computed(() => {
  if (!props.member || !props.member.activities) return new Set()
  return new Set(props.member.activities.map(a => a.id))
})

const fetchAllActivities = async () => {
  try {
    isLoading.value = true
    error.value = null
    allActivities.value = await apiFetch('/activities/')
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        } finally {
          isLoading.value = false
        }
      }
  
      const handleCheckboxChange = async (activity, isChecked) => {
        if (!props.member) return
        const url = `/members/${props.member.id}/activities/${activity.id}`
        const method = isChecked ? 'POST' : 'DELETE'
        try {
          const updatedMember = await apiFetch(url, { method })
          emit('update:member', updatedMember)
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            alert(`Error al actualizar la actividad: ${e.message}`)
          }
        }
      }
onMounted(() => {
  if (props.show) {
    fetchAllActivities()
  }
})
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Actividades de: {{ member?.first_name }} {{ member?.last_name }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="isLoading" class="text-center">
            <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <div v-if="!isLoading && !error">
            <p>Selecciona las actividades en las que participa el socio.</p>
            <div v-for="activity in allActivities" :key="activity.id" class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                :id="`activity-${activity.id}`"
                :checked="memberActivityIds.has(activity.id)"
                @change="handleCheckboxChange(activity, $event.target.checked)"
              >
              <label class="form-check-label" :for="`activity-${activity.id}`">
                {{ activity.name }} ($ {{ $formatCurrency(activity.monthly_cost) }})
              </label>
            </div>
            <div v-if="allActivities.length === 0">
              <p class="text-muted">No hay actividades disponibles para inscribir.</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
