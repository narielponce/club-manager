<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Estado de Cuenta de Mis Alumnos</h1>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando informe...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-if="!isLoading && !error" class="card shadow-sm">
      <div class="card-header">
        <h3>Saldos de Alumnos</h3>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle">
            <thead>
              <tr>
                <th scope="col">Alumno</th>
                <th scope="col">DNI</th>
                <th scope="col" class="text-end">Saldo</th>
                <th scope="col" class="text-end" style="width: 150px;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in reportData" :key="student.member_id">
                <td>{{ student.first_name }} {{ student.last_name }}</td>
                <td>{{ student.dni || 'N/A' }}</td>
                <td class="text-end" :class="getBalanceClass(student.balance)">
                  {{ $formatCurrency(student.balance) }}
                </td>
                <td class="text-end">
                  <button @click="openStatementModal(student)" class="btn btn-outline-info btn-sm">Ver Detalle</button>
                </td>
              </tr>
              <tr v-if="reportData.length === 0">
                <td colspan="4" class="text-center text-muted">No se encontraron alumnos en tus actividades.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Account Statement Modal for detail view -->
    <MemberStatementModal
      v-if="isStatementModalVisible"
      :show="isStatementModalVisible"
      :member-id="selectedStudent?.member_id"
      :member-name="`${selectedStudent?.first_name} ${selectedStudent?.last_name}`"
      @close="closeStatementModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { apiFetch } from '../services/api.js';
import MemberStatementModal from '../components/MemberStatementModal.vue';

const reportData = ref([]);
const isLoading = ref(true);
const error = ref(null);

const isStatementModalVisible = ref(false);
const selectedStudent = ref(null);

const fetchReport = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiFetch('/reports/my-students/account-status');
    reportData.value = response.students;
  } catch (e) {
    if (e.name !== 'SessionExpiredError') {
      error.value = 'Error al cargar el informe: ' + e.message;
    }
  } finally {
    isLoading.value = false;
  }
};

const openStatementModal = (student) => {
  selectedStudent.value = student;
  isStatementModalVisible.value = true;
};

const closeStatementModal = () => {
  isStatementModalVisible.value = false;
  selectedStudent.value = null;
};

const getBalanceClass = (balance) => {
  if (balance > 0) return 'text-danger fw-bold'; // Deudor
  if (balance < 0) return 'text-success'; // A favor
  return 'text-muted';
};

onMounted(fetchReport);
</script>
