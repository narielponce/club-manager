<script setup>
import { ref, onMounted } from 'vue'
import AddMemberForm from '../components/AddMemberForm.vue'
import MembersList from '../components/MembersList.vue'
import MemberPaymentsModal from '../components/MemberPaymentsModal.vue'
import MemberActivitiesModal from '../components/MemberActivitiesModal.vue'
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

// --- Payments Modal State ---
const isPaymentsModalVisible = ref(false)
const selectedMemberForPayments = ref(null)

const openPaymentsModal = (member) => {
  selectedMemberForPayments.value = member
  isPaymentsModalVisible.value = true
}

const closePaymentsModal = () => {
  isPaymentsModalVisible.value = false
}

// --- Activities Modal State ---
const isActivitiesModalVisible = ref(false)
const selectedMemberForActivities = ref(null)

const openActivitiesModal = (member) => {
  selectedMemberForActivities.value = member
  isActivitiesModalVisible.value = true
}

const closeActivitiesModal = () => {
  isActivitiesModalVisible.value = false
}

// When the modal updates the member, we update our local list to match
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
    </div>

    <AddMemberForm @member-added="handleMembersChanged" />
    
    <hr class="my-4">

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
    <MemberPaymentsModal
      v-if="isPaymentsModalVisible"
      :show="isPaymentsModalVisible"
      :member-id="selectedMemberForPayments?.id"
      :member-name="`${selectedMemberForPayments?.first_name} ${selectedMemberForPayments?.last_name}`"
      @close="closePaymentsModal"
    />

    <MemberActivitiesModal
      v-if="isActivitiesModalVisible"
      :show="isActivitiesModalVisible"
      :member="selectedMemberForActivities"
      @close="closeActivitiesModal"
      @update:member="handleMemberUpdateFromModal"
    />
  </div>
</template>
