<template>
  <div>
    <!-- Vertical Sidebar (Visible on large screens) -->
    <div class="sidebar bg-dark text-white vh-100 p-3 d-none d-lg-flex flex-column">
      <div class="text-center">
        <!-- Logo and client name/user role display -->
        <img :src="defaultLogo" alt="Logo" class="mb-3" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">
        <div v-if="currentUser" class="text-white text-truncate">
          <span v-if="currentUser.role === 'superadmin'" title="Panel de Superadministrador">
            Panel Superadmin
          </span>
          <span v-else-if="currentUser.client" :title="currentUser.client.name">
            {{ currentUser.client.name }}
          </span>
          <span v-else-if="currentUser.role === 'client'" title="Panel de Usuario">
            Mi Panel
          </span>
        </div>
      </div>
      <hr>
      <ul class="nav nav-pills flex-column mb-auto">
        <!-- Example for a new dashboard link -->
        <li v-if="currentUser?.role === 'client'" class="nav-item">
          <router-link to="/" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-speedometer2 me-2" viewBox="0 0 16 16">
              <path d="M8 4a.5.5 0 0 1 .5.5V6a.5.5 0 0 1-1 0V4.5A.5.5 0 0 1 8 4z"/>
              <path fill-rule="evenodd" d="M12.293 2.293A8 8 0 1 0 3.707 13.707.5.5 0 0 1 3 13.354 7 7 0 1 1 12.646 2.646a.5.5 0 0 1-.353-.353zM8 11A3 3 0 1 1 8 5a3 3 0 0 1 0 6z"/>
            </svg>
            Dashboard
          </router-link>
        </li>
        <!-- Superadmin Dashboard -->
        <li v-if="currentUser?.role === 'superadmin'" class="nav-item">
          <router-link to="/superadmin/dashboard" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-person-workspace me-2" viewBox="0 0 16 16">
              <path d="M4 16s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H4Zm4-5c1.664 0 2.514-.855 2.875-1.5-.236-.45-.487-.824-.77-1.125C9.421 8.178 8.423 8 8 8c-1.664 0-2.514.855-2.875 1.5.236.45.487.824.77 1.125C6.579 10.822 7.577 11 8 11Z"/>
              <path d="M2 1.5a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5ZM.5 3a.5.5 0 0 1 .5-.5h15a.5.5 0 0 1 0 1H1a.5.5 0 0 1-.5-.5ZM1.5 5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5ZM.5 7a.5.5 0 0 1 .5-.5h15a.5.5 0 0 1 0 1H1a.5.5 0 0 1-.5-.5ZM1.5 9a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1H2a.5.5 0 0 1-.5-.5ZM.5 11a.5.5 0 0 1 .5-.5h15a.5.5 0 0 1 0 1H1a.5.5 0 0 1-.5-.5Z"/>
            </svg>
            Clientes
          </router-link>
        </li>
        <!-- Logout always visible if logged in -->
        <li v-if="currentUser">
          <a href="#" @click.prevent="logout" class="nav-link text-white d-flex align-items-center mt-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-box-arrow-right me-2" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
              <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
            </svg>
            Logout
          </a>
        </li>
      </ul>
    </div>

    <!-- Content Wrapper -->
    <div class="content-wrapper">
      <!-- Topbar (becomes collapsible on small screens) -->
      <nav class="navbar navbar-expand-lg navbar-light bg-white topbar static-top shadow">
        <div class="container-fluid">
          <!-- Mobile Navbar Brand -->
          <router-link to="/" class="navbar-brand d-flex align-items-center d-lg-none">
            <img :src="defaultLogo" alt="Logo" width="30" height="30" class="d-inline-block align-text-top rounded-circle me-2">
            <span v-if="currentUser && currentUser.client" class="fs-6 text-truncate" style="max-width: 150px;">
              {{ currentUser.client.name }}
            </span>
             <span v-else-if="currentUser?.role === 'superadmin'" class="fs-6">
              Superadmin
            </span>
          </router-link>

          <!-- Hamburger Toggler (Visible on small screens) -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbarCollapse"
            aria-controls="mainNavbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>

          <!-- Collapsible wrapper -->
          <div class="collapse navbar-collapse" id="mainNavbarCollapse">
            <!-- Mobile Nav Links -->
            <ul class="navbar-nav mb-2 mb-lg-0">
               <li v-if="currentUser?.role === 'client'" class="nav-item d-lg-none">
                <router-link to="/" class="nav-link" active-class="active">Dashboard</router-link>
              </li>
              <li v-if="currentUser?.role === 'superadmin'" class="nav-item d-lg-none">
                <router-link to="/superadmin/dashboard" class="nav-link" active-class="active">Clientes</router-link>
              </li>
              <li v-if="currentUser" class="nav-item d-lg-none">
                <a href="#" @click.prevent="logout" class="nav-link">Logout</a>
              </li>
            </ul>

            <!-- User Info (pushes to the right on desktop) -->
            <div class="navbar-nav ms-auto" v-if="currentUser">
              <span class="navbar-text text-secondary small">Bienvenido, {{ currentUser.email }}</span>
            </div>
          </div>
        </div>
      </nav>
      <!-- End of Topbar -->

      <!-- Main Content -->
      <div class="main-content p-4">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { logout } from '../services/auth.js'
import { currentUser } from '../services/user.js'
import { RouterLink } from 'vue-router'

const defaultLogo = "data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='30' fill='%23495057'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='24' font-family='sans-serif' dy='.1em'%3EPEM%3C/text%3E%3C/svg%3E"; // Personal Expense Manager

// logoSrc is no longer dynamic based on club, as clients don't have logos
// if the superadmin gets a logo, it can be added here
const logoSrc = computed(() => {
  return defaultLogo;
});

// Roles will be 'superadmin' and 'client' for this project
// Remove all old role checks
// const isAdmin = computed(() => currentUser.value?.role === 'admin')
// const canViewMembers = computed(() => {
//   const role = currentUser.value?.role
//   return role === 'admin' || role === 'tesorero' || role === 'profesor'
// })
// const canAccessFinancesView = computed(() => {
//   const role = currentUser.value?.role
//   return role === 'admin' || role === 'tesorero' || role === 'profesor'
// })

// const canManageFinances = computed(() => {
//   const role = currentUser.value?.role
//   return role === 'admin' || role === 'tesorero' || role === 'profesor'
// })

// const isFinanceAdmin = computed(() => {
//   const role = currentUser.value?.role
//   return role === 'admin' || role === 'tesorero'
// })

// const isProfessor = computed(() => {
//   const role = currentUser.value?.role
//   return role === 'profesor'
// })
</script>

<style scoped>
.sidebar {
  width: 280px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.content-wrapper {
}

/* Desktop view */
@media (min-width: 992px) {
  .content-wrapper {
    margin-left: 280px;
    /* Same as sidebar width */
  }
}

/* Mobile view */
@media (max-width: 991.98px) {
  .content-wrapper {
    margin-left: 0;
  }
}


/* Style for router-link */
.nav-link.active {
  font-weight: bold;
}

/* Ensure mobile menu scrolls if content overflows */
#mainNavbarCollapse.collapse:not(.show) {
    display: none;
}
@media (max-width: 991.98px) {
  #mainNavbarCollapse {
    overflow-y: auto;
    max-height: calc(100vh - 100px); /* Adjust based on your topbar height */
  }
}
</style>