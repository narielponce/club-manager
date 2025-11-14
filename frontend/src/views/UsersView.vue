<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../services/api.js'
import UserList from '../components/UserList.vue'
import AddUserModal from '../components/AddUserModal.vue'

const users = ref([])
const clubSettings = ref(null)
const error = ref(null)
const isLoading = ref(true)
const isAddModalVisible = ref(false)

const fetchData = async () => {
  try {
    isLoading.value = true
    error.value = null
    // Fetch both in parallel
    const [usersData, settingsData] = await Promise.all([
      apiFetch('/club/users/'),
      apiFetch('/club/settings'),
    ])
    users.value = usersData
    clubSettings.value = settingsData
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        } finally {
          isLoading.value = false
        }
      }
onMounted(fetchData)

const handleUsersChanged = () => {
  // Optionally close the modal on success and refresh the list
  isAddModalVisible.value = false
  fetchData() // Refetch all data
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de Usuarios</h1>
      <button class="btn btn-primary" @click="isAddModalVisible = true">Nuevo Usuario</button>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando usuarios...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <UserList
      v-if="!isLoading && !error"
      :users="users"
      @user-updated="handleUsersChanged"
      @user-deleted="handleUsersChanged"
    />

    <AddUserModal
      :show="isAddModalVisible"
      :email-domain="clubSettings?.email_domain"
      @close="isAddModalVisible = false"
      @user-added="handleUsersChanged"
    />
  </div>
</template>
