<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import MembersList from '../components/MembersList.vue'
import MemberStatementModal from '../components/MemberStatementModal.vue'
import MemberActivitiesModal from '../components/MemberActivitiesModal.vue'
import AddMemberModal from '../components/AddMemberModal.vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

const members = ref([])
const error = ref(null)
const isLoading = ref(true)
const activities = ref([])

// --- Role-based access control ---
const isAdmin = computed(() => currentUser.value?.role === 'admin')

// --- Filter & Sort State ---
const searchQuery = ref('')
const searchTerm = ref('')
const selectedActivityId = ref(null)
const sortBy = ref('last_name') // Default sort

// --- Pagination State ---
const currentPage = ref(1)
const pageSize = ref(10)
const totalMembers = ref(0)

const totalPages = computed(() => {
  return Math.ceil(totalMembers.value / pageSize.value)
})

// --- Data Fetching ---
const fetchMembers = async () => {
  try {
    isLoading.value = true
    error.value = null
    let url = `/members?page=${currentPage.value}&size=${pageSize.value}&sort_by=${sortBy.value}`
    if (searchTerm.value) {
      url += `&search=${encodeURIComponent(searchTerm.value)}`
    }
    if (selectedActivityId.value) {
      url += `&activity_id=${selectedActivityId.value}`
    }
    const data = await apiFetch(url)
    members.value = data.items
    totalMembers.value = data.total
  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = e.message
    }
  } finally {
    isLoading.value = false
  }
}

const fetchActivities = async () => {
  try {
    activities.value = await apiFetch('/activities/');
  } catch (e) {
    console.error("Failed to fetch activities for filter dropdown:", e);
  }
};

// Fetch initial data
onMounted(() => {
  fetchMembers();
  fetchActivities();
});

// --- Event Handlers ---
const handleSearch = () => {
  currentPage.value = 1
  searchTerm.value = searchQuery.value
  fetchMembers()
}

const clearSearch = () => {
  searchQuery.value = ''
  searchTerm.value = ''
  selectedActivityId.value = null
  currentPage.value = 1
  fetchMembers()
}

const handleSort = (newSortBy) => {
  sortBy.value = newSortBy;
  currentPage.value = 1;
  fetchMembers();
};

const handleMembersChanged = () => {
  // Reset to the first page if a member is added/deleted
  currentPage.value = 1
  fetchMembers()
}

const isPrinting = ref(false);

const handlePrint = async () => {
  error.value = null;
  isPrinting.value = true;

  try {
    // 1. Fetch all members that match the current filter
    let url = `/members?page=1&size=10000&sort_by=${sortBy.value}`; // High limit for size
    if (searchTerm.value) {
      url += `&search=${encodeURIComponent(searchTerm.value)}`;
    }
    if (selectedActivityId.value) {
      url += `&activity_id=${selectedActivityId.value}`;
    }
    const data = await apiFetch(url);
    const membersToPrint = data.items;

    if (membersToPrint.length === 0) {
      alert("No hay socios para imprimir con los filtros actuales.");
      isPrinting.value = false;
      return;
    }

    // 2. Generate PDF
    const doc = new jsPDF();
    
    const activityName = selectedActivityId.value 
      ? activities.value.find(a => a.id === selectedActivityId.value)?.name 
      : 'Todas las actividades';
    
    doc.text(`Listado de Socios`, 14, 16);
    doc.setFontSize(10);
    doc.text(`Filtro de Actividad: ${activityName || 'N/A'}`, 14, 22);
    doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, 14, 28);


    const tableColumn = ["DNI", "Apellido", "Nombre", "Email", "Teléfono"];
    const tableRows = [];

    membersToPrint.forEach(member => {
      const memberData = [
        member.dni,
        member.last_name,
        member.first_name,
        member.email || '-',
        member.phone_number || '-'
      ];
      tableRows.push(memberData);
    });

    autoTable(doc, {
      head: [tableColumn],
      body: tableRows,
      startY: 35,
    });

    // 3. Save the PDF
    doc.save('listado-socios.pdf');

  } catch (e) {
    if (e.name !== "SessionExpiredError") {
      error.value = "Error al generar el PDF: " + e.message;
    }
  } finally {
    isPrinting.value = false;
  }
};

const handlePageChange = (newPage) => {
  if (newPage > 0 && newPage <= totalPages.value) {
    currentPage.value = newPage
    fetchMembers()
  }
}

// Watch for changes and refetch members
watch([pageSize, selectedActivityId], () => {
  currentPage.value = 1 // Reset to first page
  fetchMembers()
})

// --- Modal State Management ---
const isAddMemberModalVisible = ref(false)
const isPaymentsModalVisible = ref(false)
const isActivitiesModalVisible = ref(false)
const selectedMember = ref(null)

const openPaymentsModal = (member) => {
  selectedMember.value = member
  isPaymentsModalVisible.value = true
}

const openActivitiesModal = (member) => {
  selectedMember.value = member
  isActivitiesModalVisible.value = true
}

const closeModal = () => {
  isAddMemberModalVisible.value = false
  isPaymentsModalVisible.value = false
  isActivitiesModalVisible.value = false
  selectedMember.value = null
}

// When a modal updates a member, we update our local list to match
const handleMemberUpdateFromModal = (updatedMember) => {
  const index = members.value.findIndex(m => m.id === updatedMember.id)
  if (index !== -1) {
    members.value[index] = updatedMember
  }
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Gestión de Socios</h1>
      <button v-if="isAdmin" class="btn btn-primary" @click="isAddMemberModalVisible = true">Nuevo Socio</button>
    </div>

    <!-- Search Form -->
    <div class="card mb-4">
      <div class="card-body">
        <form @submit.prevent="handleSearch" class="row g-3 align-items-end">
          <div class="col-md-5">
            <label for="search-input" class="form-label">Buscar</label>
            <input
              type="text"
              id="search-input"
              class="form-control"
              v-model="searchQuery"
              placeholder="Por DNI, Nombre o Apellido..."
            />
          </div>
          <div class="col-md-4">
            <label for="activity-filter" class="form-label">Filtrar por Actividad</label>
            <select id="activity-filter" class="form-select" v-model="selectedActivityId">
              <option :value="null">Todas las actividades</option>
              <option v-for="activity in activities" :key="activity.id" :value="activity.id">
                {{ activity.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button type="submit" class="btn btn-info me-2">Buscar</button>
            <button type="button" class="btn btn-secondary me-2" @click="clearSearch">Limpiar</button>
            <button type="button" class="btn btn-outline-primary" @click="handlePrint" :disabled="isPrinting">
              <span v-if="isPrinting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ isPrinting ? 'Generando...' : 'Imprimir' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando socios...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <MembersList
      v-if="!isLoading && !error"
      :members="members"
      :currentPage="currentPage"
      :totalPages="totalPages"
      :pageSize.sync="pageSize"
      :sort-by="sortBy"
      @page-change="handlePageChange"
      @sort-change="handleSort"
      @update:pageSize="(value) => pageSize = value"
      @member-updated="handleMembersChanged"
      @member-deleted="handleMembersChanged"
      @open-payments-modal="openPaymentsModal"
      @open-activities-modal="openActivitiesModal"
    />

    <!-- Modals -->
    <AddMemberModal
      :show="isAddMemberModalVisible"
      @close="closeModal"
      @member-added="handleMembersChanged"
    />

    <MemberStatementModal
      v-if="isPaymentsModalVisible"
      :show="isPaymentsModalVisible"
      :member-id="selectedMember?.id"
      :member-name="`${selectedMember?.first_name} ${selectedMember?.last_name}`"
      @close="closeModal"
    />

    <MemberActivitiesModal
      v-if="isActivitiesModalVisible"
      :show="isActivitiesModalVisible"
      :member="selectedMember"
      @close="closeModal"
      @update:member="handleMemberUpdateFromModal"
    />
  </div>
</template>
