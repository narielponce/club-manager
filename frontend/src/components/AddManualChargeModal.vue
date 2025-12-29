<template>
  <div v-if="visible" class="modal fade show d-block" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Crear Cargo Manual</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
          <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
          
          <form @submit.prevent="handleSubmit">
            <div class="mb-3 position-relative">
              <label for="member-search" class="form-label">Buscar Socio</label>
              <input 
                v-if="!form.member_id"
                type="text" 
                id="member-search" 
                class="form-control" 
                v-model="searchQuery" 
                placeholder="Escribe para buscar por nombre o DNI..."
                autocomplete="off"
              />
              <div v-if="isSearching" class="form-text">Buscando...</div>
              <ul v-if="searchResults.length > 0" class="list-group mt-1 position-absolute w-100" style="z-index: 1000;">
                <li 
                  v-for="member in searchResults" 
                  :key="member.id" 
                  class="list-group-item list-group-item-action"
                  @click="selectMember(member)"
                >
                  {{ member.first_name }} {{ member.last_name }} (DNI: {{ member.dni }})
                </li>
              </ul>
              <div v-if="selectedMemberName" class="mt-2 p-2 bg-light border rounded d-flex justify-content-between align-items-center">
                <span>Socio: <strong>{{ selectedMemberName }}</strong></span>
                <button type="button" class="btn-close" @click="clearSelectedMember" aria-label="Clear selection"></button>
              </div>
            </div>

            <div class="mb-3">
              <label for="charge_date" class="form-label">Fecha del Cargo</label>
              <input type="date" id="charge_date" class="form-control" v-model="form.charge_date" @input="clearMessages" required />
            </div>

            <div class="mb-3">
              <label for="amount" class="form-label">Importe</label>
              <input type="number" step="0.01" id="amount" class="form-control" v-model.number="form.amount" @input="clearMessages" required />
            </div>

            <div class="mb-3">
              <label for="description" class="form-label">Descripción</label>
              <input type="text" id="description" class="form-control" v-model="form.description" @input="clearMessages" required maxlength="100" />
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cerrar</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading || !form.member_id">
            <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Crear Cargo
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, defineProps, defineEmits } from 'vue';
import { apiFetch } from '../services/api';

const props = defineProps({
  visible: Boolean
});

const emit = defineEmits(['close', 'charge-created']);

// Member Search State
const searchQuery = ref('');
const searchResults = ref([]);
const selectedMemberName = ref('');
const isSearching = ref(false);
let debounceTimer = null;

const form = reactive({
  member_id: '',
  charge_date: new Date().toISOString().split('T')[0],
  amount: null,
  description: ''
});

const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

function clearMessages() {
  successMessage.value = '';
  errorMessage.value = '';
}

watch(searchQuery, (newQuery) => {
  searchResults.value = [];
  clearMessages();

  if (newQuery.length < 2) {
    isSearching.value = false;
    clearTimeout(debounceTimer);
    return;
  }
  
  isSearching.value = true;
  clearTimeout(debounceTimer);

  debounceTimer = setTimeout(async () => {
    try {
      const response = await apiFetch(`/members?search=${newQuery}&size=5`);
      searchResults.value = response.items;
    } catch (error) {
      errorMessage.value = 'Error al buscar socios: ' + error.message;
    } finally {
      isSearching.value = false;
    }
  }, 500); // 500ms debounce
});

function selectMember(member) {
  form.member_id = member.id;
  selectedMemberName.value = `${member.first_name} ${member.last_name}`;
  searchQuery.value = '';
  searchResults.value = [];
}

function clearSelectedMember() {
  form.member_id = '';
  selectedMemberName.value = '';
}

function resetForm() {
  clearSelectedMember();
  form.charge_date = new Date().toISOString().split('T')[0];
  form.amount = null;
  form.description = '';
  searchQuery.value = '';
  searchResults.value = [];
}

async function handleSubmit() {
  if (!form.member_id) {
    errorMessage.value = 'Por favor, busca y selecciona un socio.';
    return;
  }
  
  isLoading.value = true;
  clearMessages();

  try {
    await apiFetch('/debts/manual', {
      method: 'POST',
      body: JSON.stringify(form)
    });
    emit('charge-created');
    resetForm();
    successMessage.value = '¡Cargo creado con éxito! Puedes crear otro o cerrar la ventana.';
  } catch (error) {
    errorMessage.value = 'Error al crear el cargo: ' + error.message;
  } finally {
    isLoading.value = false;
  }
}

function closeModal() {
  resetForm();
  clearMessages();
  emit('close');
}

</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
.list-group-item-action {
  cursor: pointer;
}
</style>
