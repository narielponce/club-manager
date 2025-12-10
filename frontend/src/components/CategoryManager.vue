<script setup>
import { ref, onMounted, reactive } from 'vue';
import { apiFetch } from '../services/api.js';
import { showSessionModal } from '../services/session.js';

const categories = ref([]);
const isLoading = ref(true);
const error = ref(null);

// --- Modals State ---
const isModalVisible = ref(false);
const isEditMode = ref(false);
const selectedCategory = ref(null);

// --- Form State for Add/Edit ---
const form = reactive({
  name: '',
  type: 'income',
});

const formError = ref(null);

// --- Data Fetching ---
const fetchCategories = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    categories.value = await apiFetch('/categories/');
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = e.message;
    }
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchCategories);

// --- Add/Edit Category Logic ---
const openAddModal = () => {
  isEditMode.value = false;
  selectedCategory.value = null;
  form.name = '';
  form.type = 'income';
  formError.value = null;
  isModalVisible.value = true;
};

const openEditModal = (category) => {
  isEditMode.value = true;
  selectedCategory.value = category;
  form.name = category.name;
  form.type = category.type;
  formError.value = null;
  isModalVisible.value = true;
};

const closeModal = () => {
  isModalVisible.value = false;
};

const handleFormSubmit = async () => {
  formError.value = null;
  try {
    if (isEditMode.value && selectedCategory.value) {
      await apiFetch(`/categories/${selectedCategory.value.id}`, {
        method: 'PUT',
        body: JSON.stringify(form),
      });
    } else {
      await apiFetch('/categories/', {
        method: 'POST',
        body: JSON.stringify(form),
      });
    }
    fetchCategories();
    closeModal();
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      formError.value = e.message;
    }
  }
};

// --- Delete Category Logic ---
const handleDelete = async (categoryId) => {
  if (!confirm('¿Estás seguro de que quieres eliminar esta categoría? Esta acción no se puede deshacer y fallará si hay transacciones vinculadas.')) {
    return;
  }
  try {
    await apiFetch(`/categories/${categoryId}`, {
      method: 'DELETE',
    });
    fetchCategories();
    showSessionModal("Categoría Eliminada", "La categoría ha sido eliminada con éxito.", () => {});
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      showSessionModal("Error al Eliminar", e.message, () => {});
    }
  }
};

const getCategoryTypeLabel = (type) => {
  return type === 'income' ? 'Ingreso' : 'Gasto';
};
</script>

<template>
  <div class="card shadow-sm mt-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h3>Gestionar Categorías de Gastos / Ingresos</h3>
      <button class="btn btn-primary btn-sm" @click="openAddModal">Nueva Categoría</button>
    </div>
    <div class="card-body">
      <div v-if="isLoading" class="alert alert-info">Cargando categorías...</div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!isLoading && !error">
        <table class="table table-striped table-hover align-middle">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Tipo</th>
              <th class="text-end">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td>{{ category.name }}</td>
              <td>{{ getCategoryTypeLabel(category.type) }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-primary me-2" @click="openEditModal(category)">Editar</button>
                <button class="btn btn-sm btn-danger" @click="handleDelete(category.id)">Eliminar</button>
              </td>
            </tr>
            <tr v-if="categories.length === 0">
              <td colspan="3" class="text-center text-muted">No hay categorías definidas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Add/Edit Category Modal -->
  <div class="modal fade" :class="{ 'show': isModalVisible, 'd-block': isModalVisible }" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditMode ? 'Editar Categoría' : 'Crear Nueva Categoría' }}</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleFormSubmit">
            <div class="mb-3">
              <label for="category-name" class="form-label">Nombre</label>
              <input type="text" id="category-name" class="form-control" v-model="form.name" required />
            </div>
            <div class="mb-3">
              <label for="category-type" class="form-label">Tipo</label>
              <select id="category-type" class="form-select" v-model="form.type" required>
                <option value="income">Ingreso</option>
                <option value="expense">Gasto</option>
              </select>
            </div>
            <div v-if="formError" class="alert alert-danger mt-3 py-2">{{ formError }}</div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="handleFormSubmit">Guardar</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="isModalVisible" class="modal-backdrop fade show"></div>
</template>
