<script setup>
import { ref, watch } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
  emailDomain: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'user-added'])

const emailLocalPart = ref('')
const password = ref('')
const role = ref('')
const message = ref('')
const error = ref(null)

const availableRoles = ['tesorero', 'comision', 'profesor', 'socio']

const resetForm = () => {
  emailLocalPart.value = ''
  password.value = ''
  role.value = ''
  message.value = ''
  error.value = null
}

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
        email_local_part: emailLocalPart.value,
        password: password.value,
        role: role.value,
      }),
    })
    message.value = 'Usuario creado con éxito! Puedes cerrar o añadir otro.'
    // Clear fields for next entry, but keep modal open
    emailLocalPart.value = ''
    password.value = ''
    role.value = ''
    emit('user-added')
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        }
      }
watch(() => props.show, (newVal) => {
  if (!newVal) {
    setTimeout(() => {
      resetForm()
    }, 200)
  }
})
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Crear Nuevo Usuario</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="modal-user-email" class="form-label">Email</label>
              <div class="input-group">
                <input type="text" id="modal-user-email" class="form-control" v-model="emailLocalPart" required />
                <span class="input-group-text">@{{ emailDomain }}</span>
              </div>
            </div>
            <div class="mb-3">
              <label for="modal-user-password" class="form-label">Contraseña</label>
              <input type="password" id="modal-user-password" class="form-control" v-model="password" required />
            </div>
            <div class="mb-3">
              <label for="modal-user-role" class="form-label">Rol</label>
              <select id="modal-user-role" class="form-select" v-model="role" required>
                <option disabled value="">Seleccione un rol</option>
                <option v-for="r in availableRoles" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">Guardar Usuario</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
