<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import MembersList from '../components/MembersList.vue'
import MemberStatementModal from '../components/MemberStatementModal.vue'
import MemberActivitiesModal from '../components/MemberActivitiesModal.vue'
import AddMemberModal from '../components/AddMemberModal.vue'
import { apiFetch } from '../services/api.js'
import { currentUser } from '../services/user.js'

const members = ref([])
const error = ref(null)
const isLoading = ref(true)

// --- Role-based access control ---
const isAdmin = computed(() => currentUser.value?.role === 'admin')

// --- Search State ---
const searchQuery = ref('') // For the input field
const searchTerm = ref('')  // The actual term being searched

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
    let url = `/members?page=${currentPage.value}&size=${pageSize.value}`
    if (searchTerm.value) {
      url += `&search=${encodeURIComponent(searchTerm.value)}`
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
// Fetch members when the component is first mounted
onMounted(fetchMembers)

// --- Event Handlers ---
const handleSearch = () => {
  currentPage.value = 1
  searchTerm.value = searchQuery.value
  fetchMembers()
}

const clearSearch = () => {
  searchQuery.value = ''
  searchTerm.value = ''
  currentPage.value = 1
  fetchMembers()
}

const handleMembersChanged = () => {
  // Reset to the first page if a member is added/deleted
  currentPage.value = 1
  fetchMembers()
}

const handlePageChange = (newPage) => {
  if (newPage > 0 && newPage <= totalPages.value) {
    currentPage.value = newPage
    fetchMembers()
  }
}

// Watch for changes in pageSize and refetch members
watch(pageSize, () => {
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
        <form @submit.prevent="handleSearch" class="row g-3 align-items-center">
          <div class="col-auto flex-grow-1">
            <label for="search-input" class="visually-hidden">Buscar por DNI o Apellido</label>
            <input
              type="text"
              id="search-input"
              class="form-control"
              v-model="searchQuery"
              placeholder="Buscar por DNI o Apellido..."
            />
          </div>
          <div class="col-auto">
            <button type="submit" class="btn btn-info">Buscar</button>
          </div>
          <div class="col-auto">
            <button type="button" class="btn btn-secondary" @click="clearSearch">Limpiar</button>
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
      @page-change="handlePageChange"
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
