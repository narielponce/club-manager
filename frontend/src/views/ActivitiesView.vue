<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../services/api.js'
import ActivityList from '../components/ActivityList.vue'
import AddActivityModal from '../components/AddActivityModal.vue'

const activities = ref([])
const error = ref(null)
const isLoading = ref(true)
const isAddModalVisible = ref(false)

const fetchActivities = async () => {
  try {
    isLoading.value = true
    error.value = null
    activities.value = await apiFetch('/activities/')
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        } finally {
          isLoading.value = false
        }
      }
onMounted(fetchActivities)

const handleActivitiesChanged = () => {
  // Close modal on success and refresh list
  isAddModalVisible.value = false
  fetchActivities()
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de Actividades</h1>
      <button class="btn btn-primary" @click="isAddModalVisible = true">Nueva Actividad</button>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando actividades...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <ActivityList
      v-if="!isLoading && !error"
      :activities="activities"
      @activity-updated="handleActivitiesChanged"
      @activity-deleted="handleActivitiesChanged"
    />

    <AddActivityModal
      :show="isAddModalVisible"
      @close="isAddModalVisible = false"
      @activity-added="handleActivitiesChanged"
    />
  </div>
</template>
