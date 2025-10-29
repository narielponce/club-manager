<script setup>
import { ref, reactive, watch } from 'vue'
import { apiFetch } from '../services/api.js'

const props = defineProps({
  show: Boolean,
  memberId: Number,
  memberName: String,
})

const emit = defineEmits(['close'])

const payments = ref([])
const error = ref(null)
const isLoading = ref(false)

// --- Data Fetching ---
const fetchPayments = async () => {
  if (!props.memberId) return
  try {
    isLoading.value = true
    error.value = null
    payments.value = await apiFetch(`/members/${props.memberId}/payments/`)
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

// Watch for the modal to open and fetch data
watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchPayments()
  }
})

// --- New Payment Form ---
const newPayment = reactive({
  amount: '',
  payment_date: new Date().toISOString().slice(0, 10), // Default to today
  month_covered: '',
})
const formError = ref(null)

const handleAddPayment = async () => {
  formError.value = null
  if (!newPayment.amount || !newPayment.payment_date || !newPayment.month_covered) {
    formError.value = "Todos los campos son requeridos."
    return
  }
  try {
    await apiFetch(`/members/${props.memberId}/payments/`, {
      method: 'POST',
      body: JSON.stringify({
        amount: newPayment.amount,
        payment_date: newPayment.payment_date,
        // The month input gives YYYY-MM, but the DB expects a full date.
        // We'll standardize on the 1st of the month.
        month_covered: `${newPayment.month_covered}-01`
      }),
    })
    // Reset form and refresh list
    newPayment.amount = ''
    newPayment.month_covered = ''
    fetchPayments()
  } catch (e) {
    formError.value = e.message
  }
}
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Pagos de: {{ memberName }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="isLoading" class="text-center">
            <div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div>
          </div>
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          
          <div v-if="!isLoading && !error">
            <!-- Add Payment Form -->
            <h6>Registrar Nuevo Pago</h6>
            <form @submit.prevent="handleAddPayment" class="mb-4 p-3 border rounded bg-light">
              <div class="row align-items-end">
                <div class="col-md-3">
                  <label for="amount" class="form-label">Monto</label>
                  <input type="number" step="0.01" id="amount" class="form-control" v-model="newPayment.amount" required>
                </div>
                <div class="col-md-3">
                  <label for="payment_date" class="form-label">Fecha de Pago</label>
                  <input type="date" id="payment_date" class="form-control" v-model="newPayment.payment_date" required>
                </div>
                <div class="col-md-3">
                  <label for="month_covered" class="form-label">Mes Cubierto</label>
                  <input type="month" id="month_covered" class="form-control" v-model="newPayment.month_covered" required>
                </div>
                <div class="col-md-3">
                  <button type="submit" class="btn btn-success w-100">Añadir Pago</button>
                </div>
              </div>
              <div v-if="formError" class="alert alert-danger mt-2 py-2">{{ formError }}</div>
            </form>

            <hr class="my-4">

            <!-- Payments History Table -->
            <h6>Historial de Pagos</h6>
            <table v-if="payments.length > 0" class="table table-sm table-striped">
              <thead>
                <tr>
                  <th>Monto</th>
                  <th>Fecha de Pago</th>
                  <th>Mes Cubierto</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="payment in payments" :key="payment.id">
                  <td>{{ payment.amount }}</td>
                  <td>{{ payment.payment_date }}</td>
                  <td>{{ payment.month_covered }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else>
              <p class="text-muted">Este socio no tiene pagos registrados.</p>
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
</template>
