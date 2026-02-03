<script setup>
import { ref, onMounted, watch } from 'vue'
import { apiFetch } from '../services/api.js'
import ImputePaymentModal from './ImputePaymentModal.vue'

const props = defineProps({
  show: Boolean,
  memberId: Number,
  memberName: String,
})

const emit = defineEmits(['close'])

const statement = ref(null)
const error = ref(null)
const isLoading = ref(false)

// --- New "Impute Payment" Modal State ---
const isImputePaymentModalVisible = ref(false)
const debtToPay = ref(null)

// --- Data Fetching ---
const fetchStatement = async () => {
  if (!props.memberId) return
  try {
    isLoading.value = true
    error.value = null
    statement.value = await apiFetch(`/members/${props.memberId}/statement/`)
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message
          }
        } finally {
          isLoading.value = false
        }
      }
// Watch for the modal to become visible and then fetch data
watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchStatement()
  }
}, { immediate: true })

// --- Helper to get debt status using current account logic ---
const getDebtStatus = (debtItem) => {
  if (!statement.value) return { text: 'Calculando...', class: 'bg-light' };

  // The running balance *before* this debt was applied.
  const balance_before_debt = debtItem.balance - debtItem.amount;
  
  // The credit from previous transactions that can be applied to this debt.
  const credit_to_apply = Math.max(0, -balance_before_debt);

  // Find all payments made specifically for this debt's ID.
  const paymentsTotalForThisDebtId = statement.value.items
    .filter(i => i.debt_id === debtItem.debt_id && i.transaction_type === 'payment')
    .reduce((sum, i) => sum - i.amount, 0); // payments are negative

  const debtTotal = debtItem.amount;
  const total_covered = credit_to_apply + paymentsTotalForThisDebtId;

  // Determine status
  if (total_covered >= debtTotal) return { text: 'Pagado', class: 'bg-success' };
  // Note: A "Pago Parcial" can only happen if a direct payment was made.
  // Credit alone covering part of a debt doesn't make it "partial", it just reduces the running balance.
  if (paymentsTotalForThisDebtId > 0) return { text: 'Pago Parcial', class: 'bg-warning text-dark' };
  
  return { text: 'Impaga', class: 'bg-danger' };
}


// --- Payment Logic ---
const openImputePaymentModal = (debtId) => {
  // We need to calculate the true remaining amount for this specific debt, ignoring credit
  const debtItems = statement.value.items.filter(item => item.debt_id === debtId);
  const debtTotal = debtItems.find(item => item.transaction_type === 'debt')?.amount || 0;
  const paymentsTotal = debtItems
    .filter(item => item.transaction_type === 'payment')
    .reduce((sum, item) => sum - item.amount, 0);
  const remaining = debtTotal - paymentsTotal;

  debtToPay.value = {
    debt_id: debtId,
    remainingAmount: remaining
  };
  isImputePaymentModalVisible.value = true;
}

const handlePaymentImputed = () => {
  isImputePaymentModalVisible.value = false;
  fetchStatement(); // Refresh statement after payment
}

// --- Formatting ---
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '';
  const formatted = new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
  return value < 0 ? `- $${formatted.replace('-', '')}` : `$${formatted}`;
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC'
  });
};
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-xl modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Estado de Cuenta: {{ memberName }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="isLoading" class="text-center py-5">
            <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <div v-if="!isLoading && !error && statement">
            <!-- Desktop View: Table -->
            <div class="table-responsive d-none d-lg-block">
              <table class="table table-sm table-hover align-middle">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Concepto</th>
                    <th class="text-end">Importe</th>
                    <th class="text-end">Saldo</th>
                    <th>Estado Deuda</th>
                    <th class="text-end">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in statement.items" :key="index">
                    <td>{{ formatDate(item.transaction_date) }}</td>
                    <td>{{ item.concept }}</td>
                    <td class="text-end" :class="item.amount < 0 ? 'text-success' : 'text-danger'">
                      {{ formatCurrency(item.amount) }}
                    </td>
                    <td class="text-end fw-bold">{{ formatCurrency(item.balance) }}</td>
                    
                    <!-- Status and Action only for DEBT rows -->
                    <template v-if="item.transaction_type === 'debt'">
                      <td>
                        <span class="badge" :class="getDebtStatus(item).class">
                          {{ getDebtStatus(item).text }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button 
                          v-if="getDebtStatus(item).text !== 'Pagado'"
                          @click="openImputePaymentModal(item.debt_id)"
                          class="btn btn-success btn-sm"
                        >
                          Imputar Pago
                        </button>
                      </td>
                    </template>
                    <!-- Empty cells for PAYMENT rows -->
                    <template v-else>
                      <td></td>
                      <td></td>
                    </template>
                  </tr>
                  <tr v-if="!statement.items || statement.items.length === 0">
                    <td colspan="6" class="text-center text-muted">No hay movimientos en la cuenta.</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="border-top-2">
                    <td colspan="3" class="text-end fw-bold">Saldo Final:</td>
                    <td class="text-end fw-bolder fs-5">{{ formatCurrency(statement.final_balance) }}</td>
                    <td colspan="2"></td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- Mobile View: Cards -->
            <div class="d-block d-lg-none">
              <div v-if="!statement.items || statement.items.length === 0" class="text-center text-muted">
                  No hay movimientos en la cuenta.
              </div>
              <div v-else>
                <div v-for="(item, index) in statement.items" :key="`mobile-${index}`" class="card mb-2">
                    <div class="card-body pb-2">
                        <!-- Main Info -->
                        <div class="d-flex justify-content-between align-items-start">
                            <span class="fw-bold">{{ item.concept }}</span>
                            <span class="fw-bold" :class="item.amount < 0 ? 'text-success' : 'text-danger'">
                                {{ formatCurrency(item.amount) }}
                            </span>
                        </div>
                        <!-- Sub Info -->
                        <div class="d-flex justify-content-between text-muted small mt-1">
                            <span>{{ formatDate(item.transaction_date) }}</span>
                            <span>Saldo: {{ formatCurrency(item.balance) }}</span>
                        </div>

                        <!-- Debt-specific info -->
                        <template v-if="item.transaction_type === 'debt'">
                            <hr class="my-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <span class="badge" :class="getDebtStatus(item).class">
                                        {{ getDebtStatus(item).text }}
                                    </span>
                                </div>
                                <button 
                                    v-if="getDebtStatus(item).text !== 'Pagado'"
                                    @click="openImputePaymentModal(item.debt_id)"
                                    class="btn btn-success btn-sm"
                                >
                                    Imputar Pago
                                </button>
                            </div>
                        </template>
                    </div>
                </div>
                <!-- Footer with final balance -->
                <div class="d-flex justify-content-end fw-bold fs-5 p-3 mt-3 border-top">
                    <span class="me-2">Saldo Final:</span>
                    <span>{{ formatCurrency(statement.final_balance) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>

  <ImputePaymentModal
    v-if="isImputePaymentModalVisible"
    :show="isImputePaymentModalVisible"
    :debt-id="debtToPay?.debt_id"
    :remaining-amount="debtToPay?.remainingAmount"
    @close="isImputePaymentModalVisible = false"
    @payment-imputed="handlePaymentImputed"
  />
</template>
