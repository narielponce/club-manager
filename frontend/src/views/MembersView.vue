<script setup>
import { ref, onMounted } from 'vue'
import MembersList from '../components/MembersList.vue'
import MemberPaymentsModal from '../components/MemberPaymentsModal.vue'
import MemberActivitiesModal from '../components/MemberActivitiesModal.vue'
import AddMemberModal from '../components/AddMemberModal.vue'
import { apiFetch } from '../services/api.js'

const members = ref([])
const error = ref(null)
const isLoading = ref(true)

// --- Data Fetching ---
const fetchMembers = async () => {
  try {
    isLoading.value = true
    error.value = null
    members.value = await apiFetch('/members')
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchMembers)

const handleMembersChanged = () => {
  fetchMembers()
}

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
      <button class="btn btn-primary" @click="isAddMemberModalVisible = true">Añadir Socio</button>
    </div>

    <div v-if="isLoading" class="alert alert-info">Cargando socios...</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <MembersList
      v-if="!isLoading && !error"
      :members="members"
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

    <MemberPaymentsModal
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
