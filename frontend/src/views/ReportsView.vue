<script setup>
import { ref, onMounted } from 'vue';
import { apiFetch } from '../services/api';

const reportData = ref(null);
const loading = ref(true);
const error = ref(null);

const now = new Date();
const year = ref(now.getFullYear());
const month = ref(now.getMonth() + 1);

const months = [
  { value: 1, name: 'Enero' }, { value: 2, name: 'Febrero' }, { value: 3, name: 'Marzo' },
  { value: 4, name: 'Abril' }, { value: 5, name: 'Mayo' }, { value: 6, name: 'Junio' },
  { value: 7, name: 'Julio' }, { value: 8, name: 'Agosto' }, { value: 9, name: 'Septiembre' },
  { value: 10, name: 'Octubre' }, { value: 11, name: 'Noviembre' }, { value: 12, name: 'Diciembre' }
];

const formatCurrency = (value) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'ARS' }).format(value);

const fetchReport = async () => {
  try {
    loading.value = true;
    error.value = null;
    reportData.value = null;
    
    const url = `/reports/income-by-activity?year=${year.value}&month=${month.value}`;
    reportData.value = await apiFetch(url);
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = e.message;
    }
  } finally {
    loading.value = false;
  }
};

onMounted(fetchReport);
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
        <!-- Filter Form -->
        <form @submit.prevent="fetchReport" class="row g-3 align-items-center mb-4">
          <div class="col-md-4">
            <label for="report-year" class="form-label">Año</label>
            <input type="number" id="report-year" class="form-control" v-model.number="year" placeholder="Ej: 2025">
          </div>
          <div class="col-md-4">
            <label for="report-month" class="form-label">Mes</label>
            <select id="report-month" class="form-select" v-model.number="month">
              <option v-for="m in months" :key="m.value" :value="m.value">{{ m.name }}</option>
            </select>
          </div>
          <div class="col-md-4 d-flex align-items-end">
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              Filtrar
            </button>
          </div>
        </form>
        <hr>
        <!-- Report Results -->
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
            No se encontraron ingresos para el período seleccionado.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
