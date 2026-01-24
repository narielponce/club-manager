<script setup>
import { ref, onMounted, computed } from 'vue'
import { currentUser } from '../services/user.js'
import { accessToken } from '../services/auth.js'
import { apiFetch } from '../services/api.js'
import CategoryManager from '../components/CategoryManager.vue'

// --- Role check ---
const isAdmin = computed(() => currentUser.value?.role === 'admin');

// --- Base Fee Logic ---
const baseFee = ref(0)
const baseFeeMessage = ref('')
const baseFeeError = ref(null)

// --- Backup Logic ---
const isDownloading = ref(false);
const backupError = ref(null);

// --- Lifecycle ---
onMounted(() => {
  if (currentUser.value && currentUser.value.club) {
    baseFee.value = currentUser.value.club.base_fee || 0
  }
})

// --- Methods ---
const handleBaseFeeSubmit = async () => {
  baseFeeError.value = null
  baseFeeMessage.value = ''
  try {
    const updatedClub = await apiFetch('/club/settings', {
      method: 'PUT',
      body: JSON.stringify({
        base_fee: parseFloat(baseFee.value)
      }),
    })
    baseFee.value = updatedClub.base_fee
    if (currentUser.value) {
      currentUser.value.club = updatedClub
    }
    baseFeeMessage.value = 'Cuota social actualizada con éxito!'
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
          baseFeeError.value = e.message
        }
  }
}

const downloadBackup = async () => {
  isDownloading.value = true;
  backupError.value = null;
  try {
    const response = await fetch('/api/admin/db-backup-csv', {
      headers: {
        'Authorization': `Bearer ${accessToken.value}`
      }
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Error desconocido al generar el backup.' }));
      throw new Error(errorData.detail);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    const timestamp = new Date().toISOString().slice(0, 10);
    a.download = `backup-club-${currentUser.value.club.id}-${timestamp}.zip`;
    
    document.body.appendChild(a);
    a.click();
    
    window.URL.revokeObjectURL(url);
    a.remove();

  } catch (e) {
    backupError.value = e.message;
  } finally {
    isDownloading.value = false;
  }
}
</script>

<template>
  <div>
    <h1>Configuración y Tareas</h1>

    <!-- Data Management Card (Admin Only) -->
    <template v-if="isAdmin">
      <div class="card shadow-sm mt-4">
        <div class="card-header">
          <h3>Administración de Datos</h3>
        </div>
        <div class="card-body">
          <p class="text-muted">
            Genera un respaldo completo de los datos de tu club. Se descargará un archivo .zip
            conteniendo múltiples archivos .csv (uno por cada tabla de datos: socios, actividades, deudas, etc.).
          </p>
          <button class="btn btn-info" @click="downloadBackup" :disabled="isDownloading">
            <span v-if="isDownloading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span v-if="isDownloading"> Generando...</span>
            <span v-else>Descargar Backup (CSV)</span>
          </button>
          <div v-if="backupError" class="alert alert-danger mt-3 py-2">{{ backupError }}</div>
        </div>
      </div>
    </template>

    <!-- Base Fee Card -->
    <div class="card shadow-sm mt-4">
      <div class="card-header">
        <h3>Cuota Social Base</h3>
      </div>
      <div class="card-body">
        <p class="text-muted">Importe base de cuota societaria que se le cobrará a cada socio mensualmente.</p>
        <form @submit.prevent="handleBaseFeeSubmit">
          <div class="mb-3">
            <label for="base_fee" class="form-label">Monto de la Cuota Social</label>
            <div class="input-group" style="max-width: 250px;">
              <span class="input-group-text">$</span>
              <input type="number" step="1" id="base_fee" class="form-control" v-model="baseFee" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Guardar Cambios</button>
        </form>
        <div v-if="baseFeeMessage" class="alert alert-success mt-3 py-2">{{ baseFeeMessage }}</div>
        <div v-if="baseFeeError" class="alert alert-danger mt-3 py-2">{{ baseFeeError }}</div>
      </div>
    </div>

    <!-- Category Manager Component -->
    <CategoryManager />

  </div>
</template>
