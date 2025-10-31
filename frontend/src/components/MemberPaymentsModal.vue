<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
  memberId: Number,
  memberName: String,
})

const emit = defineEmits(['close'])

const debts = ref([])
const error = ref(null)
const isLoading = ref(false)

// --- Data Fetching ---
const fetchDebts = async () => {
  if (!props.memberId) return
  try {
    isLoading.value = true
    error.value = null
    debts.value = await apiFetch(`/members/${props.memberId}/debts/`)
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (props.show) {
    fetchDebts()
  }
})

// --- Payment Logic ---
const payingDebtId = ref(null)
const paymentForm = reactive({
  payment_date: new Date().toISOString().slice(0, 10),
  receipt: null,
})
const paymentError = ref(null)

const startPayment = (debtId) => {
  payingDebtId.value = debtId
  paymentForm.payment_date = new Date().toISOString().slice(0, 10)
  paymentForm.receipt = null
  paymentError.value = null
}

const cancelPayment = () => {
  payingDebtId.value = null
}

const handleFileChange = (event) => {
  paymentForm.receipt = event.target.files[0]
}

const handleConfirmPayment = async (debtId) => {
  paymentError.value = null
  
  const formData = new FormData()
  formData.append('payment_date', paymentForm.payment_date)
  if (paymentForm.receipt) {
    formData.append('receipt', paymentForm.receipt)
  }

  try {
    await apiFetch(`/debts/${debtId}/payments/`, {
      method: 'POST',
      body: formData, // apiFetch will handle the content-type
    })
    // Refresh and close the inline form
    payingDebtId.value = null
    fetchDebts()
  } catch (e) {
    paymentError.value = e.message
  }
}

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '';
  return new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
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
          
          <div v-if="!isLoading && !error">
            <h6>Historial de Deudas</h6>
            <table class="table table-sm table-striped table-hover align-middle">
              <thead>
                <tr>
                  <th>Mes</th>
                  <th>Monto Total</th>
                  <th>Estado</th>
                  <th class="text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="debt in debts" :key="debt.id">
                  <tr>
                    <td>{{ new Date(debt.month).toLocaleString('es-ES', { month: 'long', year: 'numeric', timeZone: 'UTC' }) }}</td>
                    <td>{{ formatCurrency(debt.total_amount) }}</td>
                    <td>
                      <span class="badge" :class="debt.is_paid ? 'bg-success' : 'bg-danger'">
                        {{ debt.is_paid ? 'Pagado' : 'Pendiente' }}
                      </span>
                    </td>
                    <td class="text-end">
                      <button 
                        v-if="!debt.is_paid" 
                        @click="startPayment(debt.id)" 
                        class="btn btn-success btn-sm"
                        :disabled="payingDebtId !== null"
                      >
                        Imputar Pago
                      </button>
                    </td>
                  </tr>
                  <!-- Inline Form for Payment -->
                  <tr v-if="payingDebtId === debt.id">
                    <td colspan="4" class="p-3 bg-light">
                      <p class="fw-bold small mb-2">Confirmar Pago</p>
                      <div class="row align-items-end">
                        <div class="col-md-4">
                          <label class="form-label small">Fecha de Pago</label>
                          <input type="date" class="form-control form-control-sm" v-model="paymentForm.payment_date" />
                        </div>
                        <div class="col-md-5">
                          <label class="form-label small">Comprobante (Opcional)</label>
                          <input type="file" class="form-control form-control-sm" @change="handleFileChange" accept=".pdf,.jpg,.jpeg,.png" />
                        </div>
                        <div class="col-md-3 text-end">
                          <button @click="handleConfirmPayment(debt.id)" class="btn btn-primary btn-sm me-2">Confirmar</button>
                          <button @click="cancelPayment" class="btn btn-secondary btn-sm">Cancelar</button>
                        </div>
                      </div>
                      <div v-if="paymentError" class="alert alert-danger mt-2 py-1 px-2 small">{{ paymentError }}</div>
                    </td>
                  </tr>
                </template>
                <tr v-if="debts.length === 0">
                  <td colspan="4" class="text-center text-muted">Este socio no tiene deudas generadas.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
