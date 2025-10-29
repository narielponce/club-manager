<script setup>
import { reactive, ref } from 'vue'
import { apiFetch } from '../services/api.js'

const emit = defineEmits(['member-added'])

// Use a reactive object for the form data, which is cleaner for multiple fields
const newMember = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  dni: '',
  birth_date: ''
})

const message = ref('')
const error = ref(null)

const resetForm = () => {
  for (const key in newMember) {
    newMember[key] = ''
  }
}

const handleSubmit = async () => {
  error.value = null
  message.value = ''
  try {
    // Filter out empty optional fields so they don't get sent as empty strings
    const payload = { ...newMember }
    for (const key in payload) {
      if (payload[key] === '') {
        delete payload[key]
      }
    }

    await apiFetch('/members', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    message.value = 'Socio creado con éxito!'
    resetForm()
    emit('member-added')
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header">
      <h2>Alta Socio</h2>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleSubmit">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="first_name" class="form-label">Nombre</label>
            <input type="text" id="first_name" class="form-control" v-model="newMember.first_name" required />
          </div>
          <div class="col-md-6 mb-3">
            <label for="last_name" class="form-label">Apellido</label>
            <input type="text" id="last_name" class="form-control" v-model="newMember.last_name" required />
          </div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" id="email" class="form-control" v-model="newMember.email" required />
          </div>
          <div class="col-md-6 mb-3">
            <label for="phone" class="form-label">Teléfono</label>
            <input type="tel" id="phone" class="form-control" v-model="newMember.phone" />
          </div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="dni" class="form-label">DNI</label>
            <input type="text" id="dni" class="form-control" v-model="newMember.dni" />
          </div>
          <div class="col-md-6 mb-3">
            <label for="birth_date" class="form-label">Fecha de Nacimiento</label>
            <input type="date" id="birth_date" class="form-control" v-model="newMember.birth_date" />
          </div>
        </div>
        <button type="submit" class="btn btn-success">Añadir Socio</button>
      </form>
      <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
      <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
    </div>
  </div>
</template>
