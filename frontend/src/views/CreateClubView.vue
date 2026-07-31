<template>
   <div>
     <div class="d-flex justify-content-between align-items-center mb-4">
       <h1>Crear Nueva Organización</h1>
       <RouterLink :to="{ name: 'superadmin-dashboard' }" class="btn btn-secondary">Volver a la Lista</RouterLink>
     </div>
     <div class="card">
       <div class="card-body">
         <form @submit.prevent="handleCreateClub">
           <div v-if="error" class="alert alert-danger">{{ error }}</div>
           <div v-if="success" class="alert alert-success">{{ success }}</div>
           
           <div class="mb-3">
             <label for="clubName" class="form-label">Nombre de la Organización</label>
             <input type="text" id="clubName" class="form-control" v-model="clubName" required>
           </div>

           <div class="mb-3">
             <label for="tenantType" class="form-label">Tipo de Organización</label>
             <select id="tenantType" class="form-select" v-model="tenantType" required>
               <option value="club">Club Deportivo / Social</option>
               <option value="academy">Academia (Danza, Música, etc.)</option>
               <option value="tutoring">Clases Particulares / Mentoría</option>
             </select>
           </div>

           <div class="mb-3">
             <label for="logo" class="form-label">Logo (Opcional)</label>
             <input type="file" id="logo" class="form-control" @change="handleFileChange" accept="image/*">
           </div>
           
           <hr>
           <h5 class="mt-4">Usuario Administrador</h5>
           
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
             Crear Organización y Admin
           </button>
         </form>
       </div>
     </div>
   </div>
 </template>
 
 <script setup>
 import { ref } from 'vue';
 import { RouterLink } from 'vue-router';
 import { apiFetch } from '../services/api';
 
 const clubName = ref('');
 const tenantType = ref('club');
 const adminEmail = ref('');
 const recoveryEmail = ref('');
 const logoFile = ref(null);
 const error = ref(null);
 const success = ref(null);
 const loading = ref(false);
 
 const handleFileChange = (event) => {
   logoFile.value = event.target.files[0];
 };
 
 const handleCreateClub = async () => {
   error.value = null;
   success.value = null;
   loading.value = true;
   try {
     const formData = new FormData();
     formData.append('club_name', clubName.value);
     formData.append('email', adminEmail.value);
     formData.append('recovery_email', recoveryEmail.value);
     formData.append('tenant_type', tenantType.value);
     if (logoFile.value) {
       formData.append('logo', logoFile.value);
     }
 
     const response = await apiFetch('/users/', {
       method: 'POST',
       body: formData,
     });
     
     success.value = `¡Organización '${response.club.name}' y admin '${response.admin_user.email}' creados con éxito!
                      Contraseña temporal: ${response.temporary_password}`;
     
     clubName.value = '';
     tenantType.value = 'club';
     adminEmail.value = '';
     recoveryEmail.value = '';
     logoFile.value = null;
     document.getElementById('logo').value = '';
 
   } catch (err) {
     console.error('Error al crear el club:', err);
     error.value = err.message || 'Ocurrió un error al crear el club.';
   } finally {
     loading.value = false;
   }
 };
 </script>
