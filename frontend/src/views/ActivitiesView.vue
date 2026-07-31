<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'
import ActivityList from '../components/ActivityList.vue'
import AddActivityModal from '../components/AddActivityModal.vue'
import { useTerminology } from '../composables/useTerminology.js'

const { t } = useTerminology()

const activities = ref([])
const professors = ref([])
const error = ref(null)
const isLoading = ref(true)
const isAddModalVisible = ref(false)

const isAdmin = computed(() => currentUser.value?.role === 'admin')

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

const fetchProfessors = async () => {
  try {
    const users = await apiFetch('/club/users/');
    professors.value = users.filter(user => user.role === 'profesor');
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      console.error("Error fetching professors:", e.message);
    }
  }
}

onMounted(() => {
  fetchActivities();
  fetchProfessors();
});

const handleActivitiesChanged = () => {
  isAddModalVisible.value = false
  fetchActivities()
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de {{ t('activities') }}</h1>
      <button v-if="isAdmin" class="btn btn-primary" @click="isAddModalVisible = true">Nueva {{ t('activity') }}</button>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando {{ t('activities').toLowerCase() }}...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <ActivityList
      v-if="!isLoading && !error"
      :activities="activities"
      :professors="professors"
      @activity-updated="handleActivitiesChanged"
      @activity-deleted="handleActivitiesChanged"
    />

    <AddActivityModal
      :show="isAddModalVisible"
      :professors="professors"
      @close="isAddModalVisible = false"
      @activity-added="handleActivitiesChanged"
    />
  </div>
</template>
