<template>
  <div>
    <h1>Crear Nuevo Club</h1>
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
            <label for="adminEmail" class="form-label">Email del Admin</label>
            <input type="email" id="adminEmail" class="form-control" v-model="adminEmail" required>
          </div>
          
          <div class="mb-3">
            <label for="adminPassword" class="form-label">Password del Admin</label>
            <input type="password" id="adminPassword" class="form-control" v-model="adminPassword" required>
          </div>
          
          <button type="submit" class="btn btn-primary">Crear Club y Admin</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { createClub } from '../services/superadmin.js';

const clubName = ref('');
const adminEmail = ref('');
const adminPassword = ref('');
const logoFile = ref(null);
const error = ref(null);
const success = ref(null);

const handleFileChange = (event) => {
  logoFile.value = event.target.files[0];
};

const handleCreateClub = async () => {
  error.value = null;
  success.value = null;
  try {
    const formData = new FormData();
    formData.append('club_name', clubName.value);
    formData.append('email', adminEmail.value);
    formData.append('password', adminPassword.value);
    if (logoFile.value) {
      formData.append('logo', logoFile.value);
    }

    const newUser = await createClub(formData);
    success.value = `¡Club '${clubName.value}' y admin '${newUser.email}' creados con éxito!`;
    
    // Clear form
    clubName.value = '';
    adminEmail.value = '';
    adminPassword.value = '';
    logoFile.value = null;
    // Reset file input visually
    document.getElementById('logo').value = '';

  } catch (err) {
    error.value = err.message || 'Ocurrió un error al crear el club.';
    console.error(err);
  }
};
</script>
