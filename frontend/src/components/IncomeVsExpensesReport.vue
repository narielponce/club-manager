<script setup>
import { ref } from 'vue';
import { apiFetch } from '../services/api';
import IncomeExpenseChart from './IncomeExpenseChart.vue';

const year = ref(new Date().getFullYear());
const reportData = ref(null);
const loading = ref(false);
const error = ref(null);

const formatCurrency = (value) => new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value);

const generateReport = async () => {
  loading.value = true;
  error.value = null;
  reportData.value = null;

  try {
    const data = await apiFetch(`/reports/income-vs-expenses/${year.value}`);
    if (data && data.items) {
      reportData.value = data;
    } else {
      error.value = "No se recibieron datos válidos del servidor.";
    }
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
    <div class="row g-3 align-items-center mb-4">
      <div class="col-auto">
        <label for="year" class="col-form-label">Año:</label>
      </div>
      <div class="col-auto">
        <input type="number" id="year" class="form-control" v-model.number="year" @keyup.enter="generateReport">
      </div>
      <div class="col-auto">
        <button @click="generateReport" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ loading ? 'Generando...' : 'Generar Informe' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="alert alert-info">
      Cargando datos del informe...
    </div>
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="reportData">
      <h4 class="mt-4">Gráfico Anual</h4>
      <IncomeExpenseChart :report-data="reportData" />

      <h4 class="mt-5">Resumen Anual</h4>
      <div class="row text-center">
        <div class="col-md-4">
          <div class="card bg-light">
            <div class="card-body">
              <h6 class="card-title">Ingresos Totales</h6>
              <p class="card-text fs-4 text-success">{{ formatCurrency(reportData.annual_income) }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card bg-light">
            <div class="card-body">
              <h6 class="card-title">Gastos Totales</h6>
              <p class="card-text fs-4 text-danger">{{ formatCurrency(reportData.annual_expense) }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card bg-light">
            <div class="card-body">
              <h6 class="card-title">Balance Anual</h6>
              <p class="card-text fs-4" :class="reportData.annual_balance >= 0 ? 'text-primary' : 'text-warning'">{{ formatCurrency(reportData.annual_balance) }}</p>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-5">Detalle Mensual</h4>
      <div class="table-responsive">
        <table class="table table-striped table-hover">
          <thead>
            <tr>
              <th>Mes</th>
              <th class="text-end">Ingresos</th>
              <th class="text-end">Gastos</th>
              <th class="text-end">Balance Mensual</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in reportData.items" :key="item.month">
              <td>{{ item.month_name }}</td>
              <td class="text-end text-success">{{ formatCurrency(item.income) }}</td>
              <td class="text-end text-danger">{{ formatCurrency(item.expense) }}</td>
              <td class="text-end" :class="item.balance >= 0 ? 'text-dark' : 'text-danger'">{{ formatCurrency(item.balance) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="!loading && !error" class="alert alert-secondary">
      Seleccione un año y haga clic en "Generar Informe" para ver los datos.
    </div>
  </div>
</template>
