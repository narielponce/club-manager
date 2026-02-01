<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'
import AddManualChargeModal from '../components/AddManualChargeModal.vue'

// --- Filter State ---
const filterType = ref(null);
const filterYear = ref(null);
const filterMonth = ref(null);

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  for (let i = currentYear; i >= 2020; i--) {
    years.push(i);
  }
  return years;
});

const monthOptions = [
  { value: 1, name: 'Enero' }, { value: 2, name: 'Febrero' }, { value: 3, name: 'Marzo' },
  { value: 4, name: 'Abril' }, { value: 5, name: 'Mayo' }, { value: 6, name: 'Junio' },
  { value: 7, name: 'Julio' }, { value: 8, name: 'Agosto' }, { value: 9, name: 'Septiembre' },
  { value: 10, name: 'Octubre' }, { value: 11, name: 'Noviembre' }, { value: 12, name: 'Diciembre' },
];

// --- Role-based access control ---
const isFinanceAdmin = computed(() => {
  const role = currentUser.value?.role;
  return role === 'admin' || role === 'tesorero';
});
const isProfessor = computed(() => currentUser.value?.role === 'profesor');


// --- Modals State ---
const isDebtModalVisible = ref(false);
const isTransactionModalVisible = ref(false);
const showAddManualChargeModal = ref(false);

const handleChargeAdded = () => {
  if (isFinanceAdmin.value) {
    fetchTransactions();
    fetchAccountBalance();
  }
};

// --- Debt Generation Logic ---
const selectedMonth = ref(new Date().toISOString().slice(0, 7))
const debtMessage = ref('')
const debtError = ref(null)
const isGenerating = ref(false)

const handleDebtSubmit = async () => {
  debtError.value = null
  debtMessage.value = ''
  isGenerating.value = true
  try {
    const response = await apiFetch('/generate-monthly-debt', {
      method: 'POST',
      body: JSON.stringify({ month: selectedMonth.value }),
    })
    debtMessage.value = response.message
    setTimeout(() => {
      isDebtModalVisible.value = false;
      debtMessage.value = '';
    }, 2000);
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      debtError.value = e.message
    }
  } finally {
    isGenerating.value = false
  }
}

// --- Transactions List & Pagination Logic ---
const transactions = ref([]);
const transactionsError = ref(null);
const transactionsLoading = ref(true);
const currentPage = ref(1);
const pageSize = ref(10);
const totalTransactions = ref(0);
const accountBalance = ref({ total: 0, breakdown: {} });

const totalPages = computed(() => Math.ceil(totalTransactions.value / pageSize.value));

const fetchAccountBalance = async () => {
  try {
    accountBalance.value = await apiFetch('/transactions/balance');
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      console.error("Error fetching account balance:", e.message);
    }
  }
};

const fetchTransactions = async () => {
  try {
    transactionsLoading.value = true;
    transactionsError.value = null;
    const skip = (currentPage.value - 1) * pageSize.value;
    let url = `/transactions/?skip=${skip}&limit=${pageSize.value}`;

    if (filterType.value) {
      url += `&type=${filterType.value}`;
    }
    if (filterYear.value && filterMonth.value) {
      const year = filterYear.value;
      const month = filterMonth.value;
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const lastDay = new Date(year, month, 0).getDate();
      const endDate = `${year}-${String(month).padStart(2, '0')}-${lastDay}`;
      url += `&start_date=${startDate}&end_date=${endDate}`;
    } else if (filterYear.value) {
      const year = filterYear.value;
      const startDate = `${year}-01-01`;
      const endDate = `${year}-12-31`;
      url += `&start_date=${startDate}&end_date=${endDate}`;
    } else if (filterMonth.value) {
      const year = new Date().getFullYear();
      const month = filterMonth.value;
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const lastDay = new Date(year, month, 0).getDate();
      const endDate = `${year}-${String(month).padStart(2, '0')}-${lastDay}`;
      url += `&start_date=${startDate}&end_date=${endDate}`;
    }

    const response = await apiFetch(url);
    transactions.value = response.items;
    totalTransactions.value = response.total;
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      transactionsError.value = e.message;
    }
  } finally {
    transactionsLoading.value = false;
  }
};

const handleFilter = () => {
  currentPage.value = 1;
  fetchTransactions();
};

const clearFilters = () => {
  filterType.value = null;
  filterYear.value = null;
  filterMonth.value = null;
  currentPage.value = 1;
  fetchTransactions();
};

const handlePageChange = (newPage) => {
  if (newPage > 0 && newPage <= totalPages.value) {
    currentPage.value = newPage;
    fetchTransactions();
  }
};

// --- New Transaction Form Logic ---
const newTransactionForm = ref({
  transaction_date: new Date().toISOString().slice(0, 10),
  description: '',
  amount: 0,
  type: 'income',
  payment_method: 'Efectivo',
  category_id: null,
  receipt: null,
});
const categories = ref([]);
const newTransactionError = ref(null);
const newTransactionMessage = ref(null);
const isSubmittingTransaction = ref(false);

const fetchCategories = async () => {
  try {
    categories.value = await apiFetch('/categories/');
  } catch (e) {
    if (e.name !== "SessionExpiredError") console.error("Error fetching categories:", e.message);
  }
};

const handleReceiptFileChange = (event) => {
  newTransactionForm.value.receipt = event.target.files[0];
};

const handleNewTransactionSubmit = async () => {
  newTransactionError.value = null;
  newTransactionMessage.value = null;
  isSubmittingTransaction.value = true;

  if (newTransactionForm.value.amount <= 0) {
    newTransactionError.value = "El monto debe ser mayor a cero.";
    isSubmittingTransaction.value = false;
    return;
  }

  const formData = new FormData();
  formData.append('transaction_date', newTransactionForm.value.transaction_date);
  formData.append('description', newTransactionForm.value.description);
  formData.append('amount', newTransactionForm.value.amount);
  formData.append('type', newTransactionForm.value.type);
  formData.append('payment_method', newTransactionForm.value.payment_method);
  if (newTransactionForm.value.category_id) formData.append('category_id', newTransactionForm.value.category_id);
  if (newTransactionForm.value.receipt) formData.append('receipt', newTransactionForm.value.receipt);

  try {
    await apiFetch('/transactions/', { method: 'POST', body: formData });
    newTransactionMessage.value = 'Transacción registrada con éxito.';
    fetchTransactions();
    fetchAccountBalance();
    setTimeout(() => {
      isTransactionModalVisible.value = false;
      newTransactionMessage.value = '';
    }, 2000);
  } catch (e) {
    if (e.name !== "SessionExpiredError") newTransactionError.value = e.message;
  } finally {
    isSubmittingTransaction.value = false;
  }
};

const filteredCategories = computed(() => categories.value.filter(cat => cat.type === newTransactionForm.value.type));

// --- Utility Functions ---
const formatCurrency = (value) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'ARS' }).format(value);
const formatDate = (dateString) => new Date(dateString).toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC' });
const getCategoryTypeLabel = (type) => type === 'income' ? 'Ingreso' : 'Gasto';
const getCategoryName = (id) => categories.value.find(c => c.id === id)?.name || 'N/A';

// --- Initial Data Load ---
onMounted(() => {
  if (isFinanceAdmin.value) {
    fetchTransactions();
    fetchCategories();
    fetchAccountBalance();
  }
});
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Finanzas del Club</h1>
      <div>
        <button v-if="isFinanceAdmin || isProfessor" class="btn btn-success me-2" @click="showAddManualChargeModal = true">Generar Cargo Manual</button>
        <template v-if="isFinanceAdmin">
          <button class="btn btn-primary me-2" @click="isTransactionModalVisible = true">Registrar Transacción</button>
          <button class="btn btn-info" @click="isDebtModalVisible = true">Generar Deuda Mensual</button>
        </template>
      </div>
    </div>

    <!-- Add Manual Charge Modal -->
    <AddManualChargeModal 
      :show="showAddManualChargeModal" 
      @close="showAddManualChargeModal = false" 
      @charge-added="handleChargeAdded"
    />

    <!-- Transactions List -->
    <template v-if="isFinanceAdmin">
      <!-- Filters Card -->
      <div class="card shadow-sm mb-4">
        <div class="card-header">
          <h4>Filtros</h4>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleFilter" class="row g-3 align-items-end">
            <div class="col-md-3">
              <label for="filter-type" class="form-label">Tipo</label>
              <select id="filter-type" class="form-select" v-model="filterType">
                <option :value="null">Todos</option>
                <option value="income">Ingresos</option>
                <option value="expense">Egresos</option>
              </select>
            </div>
            <div class="col-md-3">
              <label for="filter-year" class="form-label">Año</label>
              <select id="filter-year" class="form-select" v-model="filterYear">
                <option :value="null">Cualquiera</option>
                <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label for="filter-month" class="form-label">Mes</label>
              <select id="filter-month" class="form-select" v-model="filterMonth">
                <option :value="null">Cualquiera</option>
                <option v-for="month in monthOptions" :key="month.value" :value="month.value">{{ month.name }}</option>
              </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
              <button type="submit" class="btn btn-info me-2">Filtrar</button>
              <button type="button" class="btn btn-secondary" @click="clearFilters">Limpiar</button>
            </div>
          </form>
        </div>
      </div>

      <div class="card shadow-sm mt-4">
        <div class="card-header d-flex justify-content-between align-items-center flex-wrap">
          <h3>Historial de Transacciones</h3>
          <div class="text-end">
            <h4 class="mb-0">
              Saldo Total: 
              <span :class="accountBalance.total >= 0 ? 'text-success' : 'text-danger'">
                {{ formatCurrency(accountBalance.total) }}
              </span>
            </h4>
            <small class="text-muted" v-if="Object.keys(accountBalance.breakdown).length > 0">
              ({{ Object.entries(accountBalance.breakdown).map(([key, value]) => `${key}: ${formatCurrency(value)}`).join(' - ') }})
            </small>
          </div>
        </div>
        <div class="card-body">
          <div v-if="transactionsLoading" class="alert alert-info">Cargando transacciones...</div>
          <div v-if="transactionsError" class="alert alert-danger">{{ transactionsError }}</div>
          <div v-if="!transactionsLoading && !transactionsError">
            <div class="table-responsive">
              <table class="table table-striped table-hover align-middle">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Categoría</th>
                    <th>Descripción</th>
                    <th>Forma de Pago</th>
                    <th class="text-end">Monto</th>
                    <th>Comprobante</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="transaction in transactions" :key="transaction.id">
                    <td>{{ formatDate(transaction.transaction_date) }}</td>
                    <td><span :class="transaction.type === 'income' ? 'badge bg-success' : 'badge bg-danger'">{{ getCategoryTypeLabel(transaction.type) }}</span></td>
                    <td>{{ getCategoryName(transaction.category_id) }}</td>
                    <td>{{ transaction.description }}</td>
                    <td>{{ transaction.payment_method }}</td>
                    <td class="text-end" :class="transaction.type === 'income' ? 'text-success' : 'text-danger'">{{ formatCurrency(transaction.amount) }}</td>
                    <td class="text-center"><a v-if="transaction.receipt_url" :href="`/${transaction.receipt_url}`" target="_blank">Ver</a><span v-else>-</span></td>
                  </tr>
                  <tr v-if="transactions.length === 0">
                    <td colspan="7" class="text-center text-muted">No hay transacciones registradas.</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination Controls -->
            <nav v-if="totalPages > 1" aria-label="Page navigation">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage - 1)">Anterior</a>
                </li>
                <li class="page-item disabled"><span class="page-link">Página {{ currentPage }} de {{ totalPages }}</span></li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <a class="page-link" href="#" @click.prevent="handlePageChange(currentPage + 1)">Siguiente</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>

      <!-- Generate Debt Modal -->
      <div class="modal fade" :class="{ 'show': isDebtModalVisible, 'd-block': isDebtModalVisible }" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header"><h5 class="modal-title">Generar Deuda Mensual</h5><button type="button" class="btn-close" @click="isDebtModalVisible = false"></button></div>
            <div class="modal-body">
              <p class="text-muted">Seleccionar año y mes y hacer clic en "Generar" para crear la cuota mensual de todos los socios activos.</p>
              <form @submit.prevent="handleDebtSubmit">
                <div class="mb-3"><label for="debt-month" class="form-label">Mes a Generar (AAAA-MM)</label><input type="month" id="debt-month" class="form-control" v-model="selectedMonth" required></div>
                <div v-if="debtMessage" class="alert alert-success py-2">{{ debtMessage }}</div>
                <div v-if="debtError" class="alert alert-danger py-2">{{ debtError }}</div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="isDebtModalVisible = false">Cancelar</button>
              <button type="button" class="btn btn-primary" @click="handleDebtSubmit" :disabled="isGenerating">
                <span v-if="isGenerating" class="spinner-border spinner-border-sm"></span> {{ isGenerating ? 'Generando...' : 'Generar Deuda' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- New Transaction Modal -->
      <div class="modal fade" :class="{ 'show': isTransactionModalVisible, 'd-block': isTransactionModalVisible }" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content">
            <div class="modal-header"><h5 class="modal-title">Registrar Nueva Transacción</h5><button type="button" class="btn-close" @click="isTransactionModalVisible = false"></button></div>
            <div class="modal-body">
              <form @submit.prevent="handleNewTransactionSubmit">
                <div class="row">
                  <div class="col-md-4 mb-3"><label for="transaction-date" class="form-label">Fecha</label><input type="date" id="transaction-date" class="form-control" v-model="newTransactionForm.transaction_date" required /></div>
                  <div class="col-md-4 mb-3"><label for="transaction-type" class="form-label">Tipo</label><select id="transaction-type" class="form-select" v-model="newTransactionForm.type" required><option value="income">Ingreso</option><option value="expense">Gasto</option></select></div>
                  <div class="col-md-4 mb-3"><label for="transaction-category" class="form-label">Categoría</label><select id="transaction-category" class="form-select" v-model="newTransactionForm.category_id"><option :value="null">-- Seleccionar --</option><option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option></select></div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3"><label for="transaction-description" class="form-label">Descripción</label><input type="text" id="transaction-description" class="form-control" v-model="newTransactionForm.description" required /></div>
                  <div class="col-md-6 mb-3"><label for="payment-method" class="form-label">Forma de Pago</label><select id="payment-method" class="form-select" v-model="newTransactionForm.payment_method" required><option>Efectivo</option><option>Transferencia</option></select></div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3"><label for="transaction-amount" class="form-label">Monto</label><input type="number" step="0.01" id="transaction-amount" class="form-control" v-model="newTransactionForm.amount" required /></div>
                  <div class="col-md-6 mb-3"><label for="transaction-receipt" class="form-label">Comprobante (Opcional)</label><input type="file" id="transaction-receipt" class="form-control" @change="handleReceiptFileChange" accept=".pdf,.jpg,.jpeg,.png" /></div>
                </div>
                <div v-if="newTransactionMessage" class="alert alert-success py-2">{{ newTransactionMessage }}</div>
                <div v-if="newTransactionError" class="alert alert-danger py-2">{{ newTransactionError }}</div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="isTransactionModalVisible = false">Cancelar</button>
              <button type="button" class="btn btn-primary" @click="handleNewTransactionSubmit" :disabled="isSubmittingTransaction">
                <span v-if="isSubmittingTransaction" class="spinner-border spinner-border-sm"></span> Registrar
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isDebtModalVisible || isTransactionModalVisible" class="modal-backdrop fade show"></div>
    </template>
  </div>
</template>
