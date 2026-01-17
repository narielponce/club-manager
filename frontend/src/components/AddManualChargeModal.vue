<template>
  <div class="modal fade" :class="{ 'show': show, 'd-block': show }" id="addManualChargeModal" tabindex="-1"
    aria-labelledby="addManualChargeModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addManualChargeModalLabel">Generar Cargo Manual</h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitCharge">
            <!-- Member Search -->
            <div class="mb-3">
              <label for="member-search" class="form-label">Socio</label>
              <div v-if="form.member_id" class="d-flex align-items-center">
                <input type="text" class="form-control" :value="selectedMemberName" disabled>
                <button type="button" class="btn btn-outline-secondary ms-2" @click="clearMemberSelection">X</button>
              </div>
              <div v-else class="position-relative">
                <input type="text" class="form-control" v-model="searchQuery" @focus="showResults = true"
                  placeholder="Buscar por nombre, apellido o DNI..." id="member-search">
                <div v-if="isLoadingSearch" class="spinner-border spinner-border-sm position-absolute end-0 top-50 translate-middle-y me-2" role="status">
                  <span class="visually-hidden">Buscando...</span>
                </div>
                <ul v-if="showResults && searchResults.length > 0" class="list-group position-absolute w-100" style="z-index: 1000;">
                  <li v-for="member in searchResults" :key="member.id" class="list-group-item list-group-item-action"
                    @click="selectMember(member)">
                    {{ member.first_name }} {{ member.last_name }} (DNI: {{ member.dni || 'N/A' }})
                  </li>
                </ul>
              </div>
               <input type="hidden" :value="form.member_id" required>
            </div>

            <div class="mb-3">
              <label for="date" class="form-label">Fecha</label>
              <input type="date" class="form-control" v-model="form.date" id="date" required>
            </div>
            <div class="mb-3">
              <label for="description" class="form-label">Descripción</label>
              <input type="text" class="form-control" v-model="form.description" id="description" required>
            </div>
            <div class="mb-3">
              <label for="amount" class="form-label">Monto</label>
              <input type="number" step="0.01" class="form-control" v-model="form.amount" id="amount" required>
            </div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="isSubmitting" :class="{'disabled': !form.member_id}">
                <span v-if="isSubmitting" class="spinner-border spinner-border-sm" role="status"
                  aria-hidden="true"></span>
                Guardar Cargo
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { apiFetch } from '../services/api';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close', 'charge-added']);

// Form state
const form = ref({
  member_id: null,
  date: new Date().toISOString().slice(0, 10),
  description: '',
  amount: ''
});

// Member search state
const searchQuery = ref('');
const searchResults = ref([]);
const selectedMemberName = ref('');
const isLoadingSearch = ref(false);
const showResults = ref(false);
let debounceTimer = null;

// Modal/Submission state
const isSubmitting = ref(false);
const errorMessage = ref('');

watch(searchQuery, (newValue) => {
  clearTimeout(debounceTimer);
  if (newValue.length > 1) {
    debounceTimer = setTimeout(() => {
      searchMembers(newValue);
    }, 300);
  } else {
    searchResults.value = [];
  }
});

watch(() => props.show, (show) => {
  if (show) {
    resetForm();
  }
});

function closeModal() {
  emit('close');
}

async function searchMembers(query) {
  isLoadingSearch.value = true;
  try {
    const response = await apiFetch(`/members?is_active=true&size=10&search=${query}`);
    searchResults.value = response.items;
    showResults.value = true;
  } catch (error) {
    errorMessage.value = 'Error al buscar socios.';
    console.error(error);
  } finally {
    isLoadingSearch.value = false;
  }
}

function selectMember(member) {
  form.value.member_id = member.id;
  selectedMemberName.value = `${member.first_name} ${member.last_name}`;
  searchQuery.value = '';
  searchResults.value = [];
  showResults.value = false;
}

function clearMemberSelection() {
    form.value.member_id = null;
    selectedMemberName.value = '';
    searchQuery.value = '';
}

function resetForm() {
    clearMemberSelection();
    form.value.date = new Date().toISOString().slice(0, 10);
    form.value.description = '';
    form.value.amount = '';
    errorMessage.value = '';
    isSubmitting.value = false;
}

async function submitCharge() {
  if (!form.value.member_id) {
    errorMessage.value = "Por favor, seleccione un socio.";
    return;
  }
  isSubmitting.value = true;
  errorMessage.value = '';
  try {
    const chargeData = {
      ...form.value,
      amount: parseFloat(form.value.amount)
    };
    await apiFetch('/debts/manual', {
      method: 'POST',
      body: JSON.stringify(chargeData)
    });
    emit('charge-added');
    closeModal();
  } catch (error) {
    errorMessage.value = 'Error al crear el cargo. ' + (error.message || 'Error desconocido.');
  } finally {
    isSubmitting.value = false;
  }
}
</script>
