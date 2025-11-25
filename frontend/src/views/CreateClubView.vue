<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Crear Nuevo Club</h1>
      <RouterLink :to="{ name: 'superadmin-dashboard' }" class="btn btn-secondary">Volver a la Lista</RouterLink>
    </div>
    <div class="card">
      <div class="card-body">
        <form @submit.prevent="handleCreateClub">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>
          
          <div class="mb-3">
            <label for="clubName" class="form-label">Nombre del Club</label>
            <input type="text" id="clubName" class="form-control" v-model="clubName" required>
          </div>

          <div class="mb-3">
            <label for="logo" class="form-label">Logo del Club (Opcional)</label>
            <input type="file" id="logo" class="form-control" @change="handleFileChange" accept="image/*">
          </div>
          
          <hr>
          <h5 class="mt-4">Usuario Administrador del Club</h5>
          
          <div class="mb-3">
            <label for="adminEmail" class="form-label">Email del Admin (Usuario)</label>
            <input type="email" id="adminEmail" class="form-control" v-model="adminEmail" required>
          </div>
          
          <div class="mb-3">
            <label for="recoveryEmail" class="form-label">Email de Recuperación (Real)</label>
            <input type="email" id="recoveryEmail" class="form-control" v-model="recoveryEmail" required>
            <div class="form-text">Este email se usará para recuperar la contraseña del admin.</div>
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Crear Club y Admin
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { RouterLink } from 'vue-router';
import { apiFetch } from '../services/api'; // Changed from createClub in superadmin.js

const clubName = ref('');
const adminEmail = ref('');
const recoveryEmail = ref(''); // Added
const logoFile = ref(null);
const error = ref(null);
const success = ref(null);
const loading = ref(false); // Added for button state

const handleFileChange = (event) => {
  logoFile.value = event.target.files[0];
};

const handleCreateClub = async () => {
  error.value = null;
  success.value = null;
  loading.value = true; // Set loading to true
  try {
    const formData = new FormData();
    formData.append('club_name', clubName.value);
    formData.append('email', adminEmail.value);
    formData.append('recovery_email', recoveryEmail.value); // Added recovery_email
    if (logoFile.value) {
      formData.append('logo', logoFile.value);
    }

    // Direct call to the users endpoint, as discovered
    const response = await apiFetch('/users/', {
      method: 'POST',
      body: formData, // FormData is automatically set with Content-Type: multipart/form-data
    });
    
    // API now returns ClubCreationResponse
    success.value = `¡Club '${response.club.name}' y admin '${response.admin_user.email}' creados con éxito!
                     Contraseña temporal: ${response.temporary_password}`;
    
    // Clear form
    clubName.value = '';
    adminEmail.value = '';
    recoveryEmail.value = ''; // Clear recovery email
    logoFile.value = null;
    document.getElementById('logo').value = ''; // Reset file input visually

  } catch (err) {
    console.error('Error al crear el club:', err);
    error.value = err.message || 'Ocurrió un error al crear el club.';
  } finally {
    loading.value = false; // Set loading to false
  }
};
</script>
