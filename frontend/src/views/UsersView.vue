<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../services/api.js'
import AddUserForm from '../components/AddUserForm.vue'
import UserList from '../components/UserList.vue'

const users = ref([])
const error = ref(null)
const isLoading = ref(true)

const fetchUsers = async () => {
  try {
    isLoading.value = true
    error.value = null
    users.value = await apiFetch('/club/users/')
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchUsers)

// A single handler to refresh the list for any change
const handleUsersChanged = () => {
  fetchUsers()
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de Usuarios</h1>
    </div>

    <AddUserForm @user-added="handleUsersChanged" />
    
    <hr class="my-4">

    <div v-if="isLoading" class="alert alert-info">Cargando usuarios...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <UserList
      v-if="!isLoading && !error"
      :users="users"
      @user-updated="handleUsersChanged"
      @user-deleted="handleUsersChanged"
    />
  </div>
</template>
