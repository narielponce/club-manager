<script setup>
import { ref, reactive } from 'vue'
import { apiFetch } from '../services/api.js'
import AdminChangePasswordModal from './AdminChangePasswordModal.vue'

defineProps({
  users: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['user-deleted', 'user-updated'])

// Define the roles available for editing
const availableRoles = ['admin', 'tesorero', 'comision', 'profesor', 'socio']

// --- Modal State ---
const showPasswordModal = ref(false)
const selectedUser = ref(null)

// --- Delete (Deactivate) Logic ---
const handleDelete = async (userId) => {
  if (!confirm('¿Estás seguro de que quieres desactivar este usuario?')) {
    return
  }
  try {
    await apiFetch(`/club/users/${userId}`, {
      method: 'DELETE',
    })
    emit('user-deleted')
  } catch (error) {
    if (error.name !== "SessionExpiredError") {
      alert('Error al desactivar usuario: ' + error.message)
    }
  }
}

// --- Edit Logic ---
const editingUserId = ref(null)
const editFormData = reactive({ role: '', is_active: true })

const startEditing = (user) => {
  editingUserId.value = user.id
  selectedUser.value = user // Store the whole user object
  editFormData.role = user.role
  editFormData.is_active = user.is_active
}

const cancelEditing = () => {
  editingUserId.value = null
  selectedUser.value = null // Clear selected user
}

const handleUpdate = async (userId) => {
  try {
    await apiFetch(`/club/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(editFormData),
    })
    emit('user-updated')
    editingUserId.value = null // Exit editing mode
    selectedUser.value = null
  } catch (error) {
    if (error.name !== "SessionExpiredError") {
      alert('Error al actualizar usuario: ' + error.message)
    }
  }
}
</script>

<template>
  <div>
    <div class="card shadow-sm">
      <div class="card-header">
        <h3>Usuarios del Club</h3>
      </div>
      <div class="card-body">
        <!-- Desktop view: Table -->
        <div class="table-responsive d-none d-lg-block">
          <table class="table table-striped table-hover align-middle">
            <thead>
              <tr>
                <th scope="col">Email</th>
                <th scope="col">Rol</th>
                <th scope="col">Estado</th>
                <th scope="col" class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <template v-if="editingUserId !== user.id">
                  <td>{{ user.email }}</td>
                  <td>{{ user.role }}</td>
                  <td>
                    <span :class="user.is_active ? 'text-success' : 'text-danger'">
                      {{ user.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button @click="startEditing(user)" class="btn btn-primary btn-sm me-2">Editar</button>
                    <button v-if="user.is_active" @click="handleDelete(user.id)"
                      class="btn btn-warning btn-sm">Desactivar</button>
                  </td>
                </template>
                <template v-else>
                  <td>{{ user.email }}</td>
                  <td>
                    <select v-model="editFormData.role" class="form-select form-select-sm">
                      <option v-for="r in availableRoles" :key="r" :value="r">{{ r }}</option>
                    </select>
                  </td>
                  <td>
                    <select v-model="editFormData.is_active" class="form-select form-select-sm">
                      <option :value="true">Activo</option>
                      <option :value="false">Inactivo</option>
                    </select>
                  </td>
                  <td class="text-end">
                    <button @click="showPasswordModal = true; selectedUser = user" type="button" class="btn btn-secondary btn-sm me-2">
                      Cambiar Contraseña
                    </button>
                    <button @click="handleUpdate(user.id)" class="btn btn-success btn-sm me-2">Guardar</button>
                    <button @click="cancelEditing" class="btn btn-dark btn-sm">Cancelar</button>
                  </td>
                </template>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="4" class="text-center text-muted">No hay usuarios para mostrar.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile view: Cards -->
        <div class="d-block d-lg-none">
          <div v-if="users.length === 0" class="text-center text-muted">
            No hay usuarios para mostrar.
          </div>
          <div v-for="user in users" :key="`mobile-${user.id}`" class="card mb-3">
            <!-- View Mode -->
            <template v-if="editingUserId !== user.id">
              <div class="card-body">
                <h5 class="card-title">{{ user.email }}</h5>
                <p class="card-text mb-1">
                  <strong>Rol:</strong> {{ user.role }}
                </p>
                <p class="card-text text-muted">
                  <strong>Estado:</strong>
                  <span :class="user.is_active ? 'text-success' : 'text-danger'">
                    {{ user.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </p>
              </div>
              <div class="card-footer bg-transparent d-flex justify-content-end gap-2">
                  <div class="dropdown">
                      <button class="btn btn-primary btn-sm dropdown-toggle" type="button" :id="`dropdownUserActions-${user.id}`" data-bs-toggle="dropdown" aria-expanded="false">
                          Acciones
                      </button>
                      <ul class="dropdown-menu" :aria-labelledby="`dropdownUserActions-${user.id}`">
                          <li><a class="dropdown-item" href="#" @click.prevent="startEditing(user)">Editar</a></li>
                          <template v-if="user.is_active">
                              <li><hr class="dropdown-divider"></li>
                              <li><a class="dropdown-item text-danger" href="#" @click.prevent="handleDelete(user.id)">Desactivar</a></li>
                          </template>
                      </ul>
                  </div>
              </div>
            </template>
            <!-- Edit Mode -->
            <template v-else>
              <div class="card-body">
                <h5 class="card-title">Editando Usuario: {{ user.email }}</h5>
                <div class="mb-2">
                  <label class="form-label">Rol</label>
                  <select v-model="editFormData.role" class="form-select form-select-sm">
                    <option v-for="r in availableRoles" :key="r" :value="r">{{ r }}</option>
                  </select>
                </div>
                <div class="mb-2">
                  <label class="form-label">Estado</label>
                  <select v-model="editFormData.is_active" class="form-select form-select-sm">
                    <option :value="true">Activo</option>
                    <option :value="false">Inactivo</option>
                  </select>
                </div>
              </div>
              <div class="card-footer bg-transparent d-flex justify-content-end flex-wrap gap-2">
                  <button @click="showPasswordModal = true; selectedUser = user" type="button" class="btn btn-secondary btn-sm">
                      Cambiar Contraseña
                  </button>
                  <button @click="handleUpdate(user.id)" class="btn btn-success btn-sm">Guardar</button>
                  <button @click="cancelEditing" class="btn btn-dark btn-sm">Cancelar</button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Password Change Modal -->
    <AdminChangePasswordModal v-if="showPasswordModal" :show="showPasswordModal" :user-id="selectedUser?.id"
      :user-email="selectedUser?.email" @close="showPasswordModal = false" />
  </div>
</template>
