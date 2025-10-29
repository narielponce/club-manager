<script setup>
import { ref } from 'vue'
import { apiFetch } from '../services/api.js'

const emit = defineEmits(['user-added'])

const email = ref('')
const password = ref('')
const role = ref('')
const message = ref('')
const error = ref(null)

// Define the roles available for an admin to create
const availableRoles = ['tesorero', 'comision', 'profesor', 'socio']

const handleSubmit = async () => {
  if (!role.value) {
    error.value = 'Por favor, seleccione un rol.'
    return
  }
  error.value = null
  message.value = ''
  try {
    await apiFetch('/club/users/', {
      method: 'POST',
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        role: role.value,
      }),
    })
    message.value = 'Usuario creado con éxito!'
    // Clear form
    email.value = ''
    password.value = ''
    role.value = ''
    emit('user-added')
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header">
      <h3>Crear Nuevo Usuario</h3>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleSubmit">
        <div class="row">
          <div class="col-md-4 mb-3">
            <label for="user-email" class="form-label">Email</label>
            <input type="email" id="user-email" class="form-control" v-model="email" required />
          </div>
          <div class="col-md-4 mb-3">
            <label for="user-password" class="form-label">Contraseña</label>
            <input type="password" id="user-password" class="form-control" v-model="password" required />
          </div>
          <div class="col-md-4 mb-3">
            <label for="user-role" class="form-label">Rol</label>
            <select id="user-role" class="form-select" v-model="role" required>
              <option disabled value="">Seleccione un rol</option>
              <option v-for="r in availableRoles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-success">Crear Usuario</button>
      </form>
      <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
      <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
    </div>
  </div>
</template>
