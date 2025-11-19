<script setup>
import { ref, onMounted } from 'vue';
import { apiFetch } from '../services/api';

const reportData = ref(null);
const loading = ref(true);
const error = ref(null);

const formatCurrency = (value) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'ARS' }).format(value);

onMounted(async () => {
  try {
    loading.value = true;
    reportData.value = await apiFetch('/reports/income-by-activity');
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = e.message;
    }
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Informes</h1>
    </div>

    <div class="card shadow-sm">
      <div class="card-header">
        <h3>Ingresos por Actividad</h3>
      </div>
      <div class="card-body">
        <div v-if="loading" class="alert alert-info">Generando informe...</div>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="!loading && !error">
          <div v-if="reportData && Object.keys(reportData).length > 0" class="table-responsive">
            <table class="table table-striped table-hover">
              <thead>
                <tr>
                  <th>Concepto (Actividad / Cuota)</th>
                  <th class="text-end">Ingresos Totales</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(total, concept) in reportData" :key="concept">
                  <td>{{ concept }}</td>
                  <td class="text-end text-success">{{ formatCurrency(total) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="alert alert-secondary">
            No hay suficientes datos de ingresos para generar este informe.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
