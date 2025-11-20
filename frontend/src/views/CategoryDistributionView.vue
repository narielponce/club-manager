<script setup>
import { ref } from 'vue';
import { apiFetch } from '../services/api';
import CategoryDistributionChart from '../components/CategoryDistributionChart.vue';

const reportData = ref(null);
const loading = ref(false);
const error = ref(null);

// Filter refs
const year = ref(new Date().getFullYear());
const month = ref(''); // Default to all months

const months = [
  { value: 1, name: 'Enero' }, { value: 2, name: 'Febrero' }, { value: 3, name: 'Marzo' },
  { value: 4, name: 'Abril' }, { value: 5, name: 'Mayo' }, { value: 6, name: 'Junio' },
  { value: 7, name: 'Julio' }, { value: 8, name: 'Agosto' }, { value: 9, name: 'Septiembre' },
  { value: 10, name: 'Octubre' }, { value: 11, name: 'Noviembre' }, { value: 12, name: 'Diciembre' }
];

const formatCurrency = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value);

const generateReport = async () => {
  loading.value = true;
  error.value = null;
  reportData.value = null;

  try {
    const params = new URLSearchParams();
    if (year.value) {
      params.append('year', year.value);
    }
    if (month.value) {
      params.append('month', month.value);
    }
    const queryString = params.toString();
    const url = `/reports/distribution-by-category${queryString ? '?' + queryString : ''}`;
    
    reportData.value = await apiFetch(url);

  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = `Error al generar el informe: ${e.message}`;
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Distribución por Categorías</h1>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <h5 class="card-title">Filtros</h5>
        <div class="row g-3 align-items-center">
          <div class="col-md-3">
            <label for="year" class="form-label">Año</label>
            <input type="number" id="year" class="form-control" v-model.number="year">
          </div>
          <div class="col-md-3">
            <label for="month" class="form-label">Mes</label>
            <select id="month" class="form-select" v-model="month">
              <option value="">Todos los meses</option>
              <option v-for="m in months" :key="m.value" :value="m.value">{{ m.name }}</option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button @click="generateReport" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ loading ? 'Generando...' : 'Generar Informe' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="alert alert-info">Cargando datos...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="reportData" class="card shadow-sm">
      <div class="card-body">
         <div v-if="reportData.income_by_category.length > 0 || reportData.expense_by_category.length > 0" class="row">
            <!-- Columna de Ingresos -->
            <div class="col-md-6">
              <CategoryDistributionChart 
                :chart-data="reportData.income_by_category"
                chart-title="Distribución de Ingresos"
              />
              <div class="table-responsive mt-4">
                <table class="table table-sm table-striped">
                  <thead>
                    <tr>
                      <th>Categoría de Ingreso</th>
                      <th class="text-end">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in reportData.income_by_category" :key="item.category">
                      <td>{{ item.category }}</td>
                      <td class="text-end">{{ formatCurrency(item.total) }}</td>
                    </tr>
                    <tr v-if="reportData.income_by_category.length === 0">
                      <td colspan="2" class="text-center text-muted">No hay datos de ingresos.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Columna de Gastos -->
            <div class="col-md-6">
              <CategoryDistributionChart 
                :chart-data="reportData.expense_by_category"
                chart-title="Distribución de Gastos"
              />
              <div class="table-responsive mt-4">
                <table class="table table-sm table-striped">
                  <thead>
                    <tr>
                      <th>Categoría de Gasto</th>
                      <th class="text-end">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in reportData.expense_by_category" :key="item.category">
                      <td>{{ item.category }}</td>
                      <td class="text-end">{{ formatCurrency(item.total) }}</td>
                    </tr>
                     <tr v-if="reportData.expense_by_category.length === 0">
                      <td colspan="2" class="text-center text-muted">No hay datos de gastos.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
         </div>
         <div v-else class="alert alert-secondary">
            No se encontraron datos con los filtros seleccionados.
          </div>
      </div>
    </div>
     <div v-else-if="!loading && !error" class="alert alert-light text-center">
      Seleccione los filtros y haga clic en "Generar Informe".
    </div>
  </div>
</template>
