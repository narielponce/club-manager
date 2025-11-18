<script setup>
import { ref, reactive, watch } from 'vue';
import { apiFetch } from '../services/api.js';

const props = defineProps({
  show: Boolean,
  debtId: Number,
  remainingAmount: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['close', 'payment-imputed']);

const form = reactive({
  amount: props.remainingAmount,
  payment_date: new Date().toISOString().slice(0, 10),
  payment_method: 'Efectivo', // Default value
  receipt: null,
});
const error = ref(null);
const isLoading = ref(false);

// Watch for changes in the prop to update the form when the modal is reopened
watch(() => props.remainingAmount, (newVal) => {
  form.amount = newVal;
});
watch(() => props.show, (newVal) => {
  if (newVal) {
    // Reset form when modal opens
    form.amount = props.remainingAmount;
    form.payment_date = new Date().toISOString().slice(0, 10);
    form.payment_method = 'Efectivo';
    form.receipt = null;
    error.value = null;
  }
});


const handleFileChange = (event) => {
  form.receipt = event.target.files[0];
};

const handleSubmit = async () => {
  error.value = null;
  isLoading.value = true;

  if (form.amount <= 0) {
    error.value = "El monto debe ser mayor a cero.";
    isLoading.value = false;
    return;
  }

  const formData = new FormData();
  formData.append('amount', form.amount);
  formData.append('payment_date', form.payment_date);
  formData.append('payment_method', form.payment_method);
  if (form.receipt) {
    formData.append('receipt', form.receipt);
  }

  try {
    await apiFetch(`/debts/${props.debtId}/payments/`, {
      method: 'POST',
      body: formData,
    });
    emit('payment-imputed');
    emit('close');
        } catch (e) {
          if (e.name !== "SessionExpiredError") {
            error.value = e.message;
          }
        } finally {
          isLoading.value = false;
        }
      };
</script>

<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Imputar Pago</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="payment-amount" class="form-label">Monto a Pagar</label>
              <input type="number" step="0.01" id="payment-amount" class="form-control" v-model="form.amount" required />
            </div>
            <div class="mb-3">
              <label for="payment-date" class="form-label">Fecha de Pago</label>
              <input type="date" id="payment-date" class="form-control" v-model="form.payment_date" required />
            </div>
            <div class="mb-3">
              <label for="payment-method" class="form-label">Forma de Pago</label>
              <select id="payment-method" class="form-select" v-model="form.payment_method" required>
                <option>Efectivo</option>
                <option>Transferencia</option>
              </select>
            </div>
            <div class="mb-3">
              <label for="payment-receipt" class="form-label">Comprobante (Opcional)</label>
              <input type="file" id="payment-receipt" class="form-control" @change="handleFileChange" accept=".pdf,.jpg,.jpeg,.png" />
            </div>
            <div v-if="error" class="alert alert-danger mt-3 py-2">{{ error }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')" :disabled="isLoading">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span v-else>Guardar Pago</span>
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>
