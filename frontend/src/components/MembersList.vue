<script setup>
import { ref, reactive, computed } from 'vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const canManagePayments = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'tesorero'
})
const canManageActivities = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'profesor'
})

defineProps({
  members: {
    type: Array,
    required: true
  },
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    required: true
  },
  sortBy: {
    type: String,
    required: true
  }
})

const emit = defineEmits([
  'member-deleted',
  'member-updated',
  'open-payments-modal',
  'open-activities-modal',
  'page-change',
  'update:pageSize',
  'sort-change'
])

// --- Delete Logic ---
const handleDelete = async (memberId) => {
  if (!confirm('¿Estás seguro de que quieres borrar este socio?')) {
    return
  }
  try {
    await apiFetch(`/members/${memberId}`, { method: 'DELETE' })
    emit('member-deleted')
      } catch (error) {
        if (error.name !== "SessionExpiredError") {
          alert('Error al borrar socio: ' + error.message)
        }
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
      member_type: 'N/A',
      member_number: '',
    })

    const startEditing = (member) => {
      editingMemberId.value = member.id
      editFormData.first_name = member.first_name
      editFormData.last_name = member.last_name
      editFormData.email = member.email
      editFormData.phone = member.phone
      editFormData.dni = member.dni
      editFormData.birth_date = member.birth_date
      editFormData.member_type = member.member_type || 'N/A'
      editFormData.member_number = member.member_number
    }

    const cancelEditing = () => {
      editingMemberId.value = null
    }

    const handleUpdate = async (memberId) => {
      try {
        const payload = { ...editFormData }
        // Allow empty strings to be sent to the backend to clear optional fields.
        // Only remove properties that are strictly null.
        for (const key in payload) {
          if (payload[key] === null) {
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
        if (error.name !== "SessionExpiredError") {
          alert('Error al actualizar socio: ' + error.message)
        }
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
      <!-- Desktop view: Table -->
      <div class="table-responsive d-none d-lg-block">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th @click="$emit('sort-change', 'dni')" class="sortable-header">
                DNI <span v-if="sortBy === 'dni'">▼</span>
              </th>
              <th @click="$emit('sort-change', 'last_name')" class="sortable-header">
                Apellido <span v-if="sortBy === 'last_name'">▼</span>
              </th>
              <th>Nombre</th>
              <th>N° Socio</th>
              <th>Tipo Socio</th>
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
                <td>{{ member.member_number || '-' }}</td>
                <td>{{ member.member_type || 'N/A' }}</td>
                <td>{{ member.email }}</td>
                <td>{{ formatPhoneNumber(member.phone) }}</td>
                <td class="text-end">
                  <button v-if="canManagePayments" @click="viewPayments(member)" class="btn btn-info btn-sm me-2">Estado de Cuenta</button>
                  <button v-if="canManageActivities" @click="manageActivities(member)" class="btn btn-secondary btn-sm me-2">Actividades</button>
                  <button v-if="isAdmin" @click="startEditing(member)" class="btn btn-primary btn-sm me-2">Editar</button>
                  <button v-if="isAdmin" @click="handleDelete(member.id)" class="btn btn-danger btn-sm">Borrar</button>
                </td>
              </template>
              <template v-else>
                <td><input type="text" v-model="editFormData.dni" class="form-control form-control-sm" /></td>
                <td><input type="text" v-model="editFormData.last_name" class="form-control form-control-sm" required/></td>
                <td><input type="text" v-model="editFormData.first_name" class="form-control form-control-sm" required/></td>
                <td><input type="text" v-model="editFormData.member_number" class="form-control form-control-sm" /></td>
                <td>
                  <select class="form-select form-select-sm" v-model="editFormData.member_type">
                    <option>N/A</option>
                    <option>Adherente</option>
                    <option>Deportivo</option>
                  </select>
                </td>
                <td><input type="email" v-model="editFormData.email" class="form-control form-control-sm" /></td>
                <td><input type="tel" v-model="editFormData.phone" class="form-control form-control-sm" required/></td>
                <td class="text-end">
                  <button @click="handleUpdate(member.id)" class="btn btn-success btn-sm me-2">Guardar</button>
                  <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
                </td>
              </template>
            </tr>
            <tr v-if="members.length === 0">
              <td colspan="8" class="text-center text-muted">No hay socios para mostrar.</td>
            </tr>
          </tbody>
        </table>
      </div>

       <!-- Mobile view: Cards -->
      <div class="d-block d-lg-none">
        <div v-if="members.length === 0" class="text-center text-muted mt-3">
          No hay socios para mostrar.
        </div>
        <div v-for="member in members" :key="`mobile-${member.id}`" class="card mb-3">
          <!-- View Mode -->
          <template v-if="editingMemberId !== member.id">
            <div class="card-body">
              <h5 class="card-title">{{ member.last_name }}, {{ member.first_name }}</h5>
              <h6 class="card-subtitle mb-2 text-muted">
                DNI: {{ formatDni(member.dni) }} | N° Socio: {{ member.member_number || '-' }}
              </h6>
              
              <div class="mt-3">
                <a class="btn btn-outline-secondary btn-sm" data-bs-toggle="collapse" :href="`#details-mobile-${member.id}`" role="button">
                  Ver más
                </a>
              </div>
              <div class="collapse mt-2" :id="`details-mobile-${member.id}`">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item px-0"><strong>Tipo:</strong> {{ member.member_type || 'N/A' }}</li>
                  <li class="list-group-item px-0"><strong>Email:</strong> {{ member.email || '-' }}</li>
                  <li class="list-group-item px-0"><strong>Teléfono:</strong> {{ formatPhoneNumber(member.phone) || '-' }}</li>
                </ul>
              </div>
            </div>
            <div class="card-footer bg-transparent d-flex justify-content-end align-items-center flex-wrap gap-2">
              <button v-if="canManagePayments" @click="viewPayments(member)" class="btn btn-info btn-sm">Estado de Cuenta</button>
              <button v-if="canManageActivities" @click="manageActivities(member)" class="btn btn-secondary btn-sm">Actividades</button>
              <div v-if="isAdmin" class="dropdown">
                <button class="btn btn-primary btn-sm dropdown-toggle" type="button" :id="`dropdownMenuButton-mobile-${member.id}`" data-bs-toggle="dropdown" aria-expanded="false">
                  Más
                </button>
                <ul class="dropdown-menu" :aria-labelledby="`dropdownMenuButton-mobile-${member.id}`">
                  <li><a class="dropdown-item" href="#" @click.prevent="startEditing(member)">Editar</a></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item text-danger" href="#" @click.prevent="handleDelete(member.id)">Borrar</a></li>
                </ul>
              </div>
            </div>
          </template>
          
          <!-- Edit Mode -->
          <template v-else>
            <div class="card-body">
              <h5 class="card-title">Editando Socio</h5>
              <div class="mb-2">
                <label class="form-label">Apellido</label>
                <input type="text" v-model="editFormData.last_name" class="form-control form-control-sm" required>
              </div>
              <div class="mb-2">
                <label class="form-label">Nombre</label>
                <input type="text" v-model="editFormData.first_name" class="form-control form-control-sm" required>
              </div>
              <div class="mb-2">
                <label class="form-label">DNI</label>
                <input type="text" v-model="editFormData.dni" class="form-control form-control-sm">
              </div>
              <div class="mb-2">
                <label class="form-label">N° Socio</label>
                <input type="text" v-model="editFormData.member_number" class="form-control form-control-sm">
              </div>
              <div class="mb-2">
                <label class="form-label">Tipo Socio</label>
                <select class="form-select form-select-sm" v-model="editFormData.member_type">
                  <option>N/A</option>
                  <option>Adherente</option>
                  <option>Deportivo</option>
                </select>
              </div>
              <div class="mb-2">
                <label class="form-label">Email</label>
                <input type="email" v-model="editFormData.email" class="form-control form-control-sm">
              </div>
              <div class="mb-2">
                <label class="form-label">Teléfono</label>
                <input type="tel" v-model="editFormData.phone" class="form-control form-control-sm">
              </div>
            </div>
            <div class="card-footer bg-transparent d-flex justify-content-end gap-2">
              <button @click="handleUpdate(member.id)" class="btn btn-success btn-sm">Guardar</button>
              <button @click="cancelEditing" class="btn btn-secondary btn-sm">Cancelar</button>
            </div>
          </template>
        </div>
      </div>
    </div>
    <div class="card-footer d-flex justify-content-between align-items-center">
      <div>
        <label for="pageSizeSelect" class="form-label me-2">Items por página:</label>
        <select
          id="pageSizeSelect"
          :value="pageSize"
          @change="emit('update:pageSize', parseInt($event.target.value))"
          class="form-select form-select-sm w-auto d-inline-block"
        >
          <option value="5">5</option>
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
        </select>
      </div>
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <button class="page-link" @click="emit('page-change', currentPage - 1)">Anterior</button>
          </li>
          <li class="page-item active">
             <span class="page-link">{{ currentPage }} / {{ totalPages }}</span>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <button class="page-link" @click="emit('page-change', currentPage + 1)">Siguiente</button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>
<style scoped>
.sortable-header {
  cursor: pointer;
}
.sortable-header:hover {
  background-color: #f8f9fa;
}
</style>
