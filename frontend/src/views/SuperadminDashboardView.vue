<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';
import { getClubs, deleteClub, updateClub } from '../services/superadmin.js';
import EditClubModal from '../components/EditClubModal.vue';

const clubs = ref([]);
const isLoading = ref(true);
const error = ref(null);

const isEditModalVisible = ref(false);
const selectedClub = ref(null);

const fetchData = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    clubs.value = await getClubs(true); // Pass true to include inactive clubs
  } catch (e) {
    error.value = e.message;
  } finally {
    isLoading.value = false;
  }
};

const handleDelete = async (clubId) => {
  if (!confirm('¿Estás seguro de que quieres desactivar este club?')) {
    return;
  }
  try {
    await deleteClub(clubId);
    fetchData(); // Refresh the list
  } catch (e) {
    alert('Error al desactivar el club: ' + e.message);
  }
};

const handleReactivate = async (clubId) => {
  if (!confirm('¿Estás seguro de que quieres reactivar este club?')) {
    return;
  }
  try {
    await updateClub(clubId, { is_active: true });
    fetchData(); // Refresh the list
  } catch (e) {
    alert('Error al reactivar el club: ' + e.message);
  }
}

const handleEdit = (club) => {
  selectedClub.value = { ...club };
  isEditModalVisible.value = true;
};

const handleClubUpdated = () => {
  isEditModalVisible.value = false;
  fetchData();
}

onMounted(fetchData);
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Dashboard de Superadmin</h1>
      <RouterLink to="/superadmin/create-club" class="btn btn-primary">Crear Nuevo Club</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando clubes...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="!isLoading && !error" class="card shadow-sm">
      <div class="card-header">
        <h3>Clubes Registrados</h3>
      </div>
      <div class="card-body">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre del Club</th>
              <th>Cuota Base</th>
              <th>Estado</th>
              <th class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="club in clubs" :key="club.id" :class="{ 'text-muted bg-light': !club.is_active }">
              <td>{{ club.id }}</td>
              <td>{{ club.name }}</td>
              <td>{{ club.base_fee ? `$${club.base_fee}` : 'No asignada' }}</td>
              <td>
                <span :class="club.is_active ? 'text-success' : 'text-danger'">
                  <strong>{{ club.is_active ? 'Activo' : 'Inactivo' }}</strong>
                </span>
              </td>
              <td class="text-end">
                <button @click="handleEdit(club)" class="btn btn-secondary btn-sm me-2">Editar</button>
                <button v-if="club.is_active" @click="handleDelete(club.id)" class="btn btn-warning btn-sm">Desactivar</button>
                <button v-else @click="handleReactivate(club.id)" class="btn btn-success btn-sm">Reactivar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <EditClubModal 
      v-if="isEditModalVisible"
      :show="isEditModalVisible"
      :club="selectedClub"
      @close="isEditModalVisible = false"
      @club-updated="handleClubUpdated"
    />
  </div>
</template>
