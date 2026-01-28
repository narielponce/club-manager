<script setup>
import { reactive, ref, watch } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close', 'member-added'])

const newMember = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  dni: '',
  birth_date: '',
  member_type: 'N/A',
  member_number: ''
})

const message = ref('')
const error = ref(null)

const resetForm = () => {
  newMember.first_name = ''
  newMember.last_name = ''
  newMember.email = ''
  newMember.phone = ''
  newMember.dni = ''
  newMember.birth_date = ''
  newMember.member_type = 'N/A'
  newMember.member_number = ''
  
  message.value = ''
  error.value = null
}

const handleSubmit = async () => {
  error.value = null
  message.value = ''
  try {
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
    message.value = 'Socio creado con éxito! Puedes cerrar esta ventana o añadir otro.'
    resetForm()
    emit('member-added')
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        }
      }
// Reset form when modal is closed
watch(() => props.show, (newVal) => {
  if (!newVal) {
    // Use a timeout to allow the closing animation to finish before clearing data
    setTimeout(() => {
      resetForm()
    }, 200);
  }
})
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Alta Nuevo Socio</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="modal-first_name" class="form-label">Nombre <span class="text-danger">*</span></label>
                <input type="text" id="modal-first_name" class="form-control" v-model="newMember.first_name" required />
              </div>
              <div class="col-md-6 mb-3">
                <label for="modal-last_name" class="form-label">Apellido <span class="text-danger">*</span></label>
                <input type="text" id="modal-last_name" class="form-control" v-model="newMember.last_name" required />
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="modal-phone" class="form-label">Teléfono <span class="text-danger">*</span></label>
                <input type="tel" id="modal-phone" class="form-control" v-model="newMember.phone" required />
              </div>
              <div class="col-md-6 mb-3">
                <label for="modal-email" class="form-label">Email</label>
                <input type="email" id="modal-email" class="form-control" v-model="newMember.email" />
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="modal-dni" class="form-label">DNI</label>
                <input type="text" id="modal-dni" class="form-control" v-model="newMember.dni" />
              </div>
              <div class="col-md-6 mb-3">
                <label for="modal-birth_date" class="form-label">Fecha de Nacimiento</label>
                <input type="date" id="modal-birth_date" class="form-control" v-model="newMember.birth_date" />
              </div>
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="modal-member-type" class="form-label">Tipo de Socio</label>
                <select id="modal-member-type" class="form-select" v-model="newMember.member_type">
                  <option>N/A</option>
                  <option>Adherente</option>
                  <option>Deportivo</option>
                </select>
              </div>
              <div class="col-md-6 mb-3">
                <label for="modal-member-number" class="form-label">Número de Socio</label>
                <input type="text" id="modal-member-number" class="form-control" v-model="newMember.member_number" />
              </div>
            </div>
            <div v-if="message" class="alert alert-success mt-3 py-2">{{ message }}</div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">Guardar Socio</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
