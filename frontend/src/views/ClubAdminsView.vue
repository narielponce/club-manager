<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import { getClubAdmins } from '../services/superadmin.js';
import EditSuperadminUserModal from '../components/EditSuperadminUserModal.vue';

const route = useRoute();
const admins = ref([]);
const isLoading = ref(true);
const error = ref(null);
const clubId = route.params.id;

const isEditModalVisible = ref(false);
const selectedUser = ref(null);

const fetchData = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    admins.value = await getClubAdmins(clubId);
  } catch (e) {
    error.value = e.message;
  } finally {
    isLoading.value = false;
  }
};

const openEditModal = (user) => {
  selectedUser.value = user;
  isEditModalVisible.value = true;
};

const handleUserUpdated = () => {
  isEditModalVisible.value = false;
  fetchData();
};

onMounted(fetchData);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Administradores del Club #{{ clubId }}</h1>
      <RouterLink :to="{ name: 'superadmin-dashboard' }" class="btn btn-secondary">Volver al Dashboard</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando administradores...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="!isLoading && !error" class="card shadow-sm">
      <div class="card-header">
        <h3>Listado de Administradores</h3>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Email de Recuperación</th>
                <th>Estado</th>
                <th class="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="admin in admins" :key="admin.id">
                <td>{{ admin.id }}</td>
                <td>{{ admin.email }}</td>
                <td>{{ admin.recovery_email || 'No asignado' }}</td>
                <td>
                  <span :class="admin.is_active ? 'text-success' : 'text-danger'">
                    <strong>{{ admin.is_active ? 'Activo' : 'Inactivo' }}</strong>
                  </span>
                </td>
                <td class="text-end">
                  <button @click="openEditModal(admin)" class="btn btn-primary btn-sm">Editar</button>
                </td>
              </tr>
              <tr v-if="admins.length === 0">
                  <td colspan="5" class="text-center text-muted">No se encontraron administradores para este club.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <EditSuperadminUserModal
      v-if="isEditModalVisible"
      :show="isEditModalVisible"
      :user="selectedUser"
      @close="isEditModalVisible = false"
      @user-updated="handleUserUpdated"
    />
  </div>
</template>
