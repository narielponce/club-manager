<script setup>
import { ref, reactive } from 'vue'
import { apiFetch } from '../services/api.js'

defineProps({
  members: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['member-deleted', 'member-updated', 'open-payments-modal', 'open-activities-modal'])

// --- Delete Logic ---
const handleDelete = async (memberId) => {
  if (!confirm('¿Estás seguro de que quieres borrar este socio?')) {
    return
  }
  try {
    await apiFetch(`/members/${memberId}`, { method: 'DELETE' })
    emit('member-deleted')
  } catch (error) {
    alert('Error al borrar socio: ' + error.message)
  }
}

// --- Edit Logic ---
const editingMemberId = ref(null)
const editFormData = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  dni: '',
  birth_date: '',
})

const startEditing = (member) => {
  editingMemberId.value = member.id
  editFormData.first_name = member.first_name
  editFormData.last_name = member.last_name
  editFormData.email = member.email
  editFormData.phone = member.phone
  editFormData.dni = member.dni
  editFormData.birth_date = member.birth_date
}

const cancelEditing = () => {
  editingMemberId.value = null
}

const handleUpdate = async (memberId) => {
  try {
    const payload = { ...editFormData }
    for (const key in payload) {
      if (payload[key] === '' || payload[key] === null) {
        delete payload[key]
      }
    }
    await apiFetch(`/members/${memberId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    emit('member-updated')
    editingMemberId.value = null
  } catch (error) {
    alert('Error al actualizar socio: ' + error.message)
  }
}

// --- Modals ---
const viewPayments = (member) => {
  emit('open-payments-modal', member)
}

const manageActivities = (member) => {
  emit('open-activities-modal', member)
}

const formatDni = (dni) => {
  if (!dni) return '';
  // Assuming DNI is a number or a string of digits
  return String(dni).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
};

const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return '';
  const digits = String(phoneNumber).replace(/\D/g, ''); // Remove non-digits
  if (digits.length !== 10) return phoneNumber; // Return original if not 10 digits

  // Heuristic based on common Argentine mobile number formats and examples
  if (digits.startsWith('11')) { // Buenos Aires (2-4-4)
    return digits.replace(/^(\d{2})(\d{4})(\d{4})$/, '$1-$2-$3');
  } else if (digits.startsWith('3543')) { // Villa Carlos Paz (4-2-4)
    return digits.replace(/^(\d{4})(\d{2})(\d{4})$/, '$1-$2-$3');
  } else { // Default to 3-3-4 for others, e.g., 351-XXX-XXXX
    return digits.replace(/^(\d{3})(\d{3})(\d{4})$/, '$1-$2-$3');
  }
};
</script>

<template>
  <div class="card shadow-sm">
    <div class="card-header">
      <h2>Listado de Socios</h2>
    </div>
    <div class="card-body">
      <div class="table-responsive">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th>DNI</th>
              <th>Apellido</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in members" :key="member.id">
              <template v-if="editingMemberId !== member.id">
                <td>{{ formatDni(member.dni) }}</td>
                <td>{{ member.last_name }}</td>
                <td>{{ member.first_name }}</td>
                <td>{{ member.email }}</td>
                <td>{{ formatPhoneNumber(member.phone) }}</td>
                <td class="text-end">
                                  <button @click="viewPayments(member)" class="btn btn-info btn-sm me-2">Pagos</button>
                                  <button @click="manageActivities(member)" class="btn btn-secondary btn-sm me-2">Actividades</button>
                                  <button @click="startEditing(member)" class="btn btn-primary btn-sm me-2">Editar</button>                  <button @click="handleDelete(member.id)" class="btn btn-danger btn-sm">Borrar</button>
                </td>
              </template>
              <template v-else>
                <td><input type="text" v-model="editFormData.dni" class="form-control form-control-sm" /></td>
                <td><input type="text" v-model="editFormData.last_name" class="form-control form-control-sm" /></td>
                <td><input type="text" v-model="editFormData.first_name" class="form-control form-control-sm" /></td>
                <td><input type="email" v-model="editFormData.email" class="form-control form-control-sm" /></td>
                <td><input type="tel" v-model="editFormData.phone" class="form-control form-control-sm" /></td>
                <td class="text-end">
                  <button @click="handleUpdate(member.id)" class="btn btn-success btn-sm me-2">Guardar</button>
                  <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
                </td>
              </template>
            </tr>
            <tr v-if="members.length === 0">
              <td colspan="6" class="text-center text-muted">No hay socios para mostrar.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
