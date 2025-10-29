<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../services/api.js'
import AddActivityForm from '../components/AddActivityForm.vue'
import ActivityList from '../components/ActivityList.vue'

const activities = ref([])
const error = ref(null)
const isLoading = ref(true)

const fetchActivities = async () => {
  try {
    isLoading.value = true
    error.value = null
    activities.value = await apiFetch('/activities/')
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchActivities)

// A single handler to refresh the list for any change
const handleActivitiesChanged = () => {
  fetchActivities()
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de Actividades</h1>
    </div>

    <AddActivityForm @activity-added="handleActivitiesChanged" />

    <hr class="my-4">

    <div v-if="isLoading" class="alert alert-info">Cargando actividades...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <ActivityList
      v-if="!isLoading && !error"
      :activities="activities"
      @activity-updated="handleActivitiesChanged"
      @activity-deleted="handleActivitiesChanged"
    />
  </div>
</template>
