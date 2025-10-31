<template>
  <div class="d-flex">
    <!-- Sidebar -->
    <div class="sidebar bg-dark text-white vh-100 p-3 d-flex flex-column">
      <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
        <span v-if="currentUser" class="fs-4">{{ currentUser.club.name }}</span>
        <span v-else class="fs-4">Club Manager</span>
      </a>
      <hr>
      <ul class="nav nav-pills flex-column mb-auto">
        <li class="nav-item">
          <router-link to="/" class="nav-link" active-class="active">Socios</router-link>
        </li>
        <li v-if="currentUser && currentUser.role === 'admin'" class="nav-item">
          <router-link to="/activities" class="nav-link" active-class="active">Actividades</router-link>
        </li>

        <!-- Admin-only link -->
        <li v-if="currentUser && currentUser.role === 'admin'" class="nav-item">
          <router-link to="/users" class="nav-link" active-class="active">Usuarios</router-link>
        </li>
        <li v-if="currentUser && currentUser.role === 'admin'" class="nav-item">
          <router-link to="/settings" class="nav-link" active-class="active">Configuración</router-link>
        </li>
        <!--<li>
          <a href="#" class="nav-link text-white disabled">Events (soon)</a>
        </li>-->
      </ul>
      <hr>
      <div v-if="currentUser">
        <div class="text-muted small">{{ currentUser.email }}</div>
        <a href="#" @click.prevent="logout" class="nav-link text-white d-block mt-1">
          Logout
        </a>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content flex-grow-1 p-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { logout } from '../services/auth.js'
import { currentUser } from '../services/user.js'
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.sidebar {
  width: 280px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100; /* Ensure it's on top */
}

.main-content {
  margin-left: 280px; /* Same as sidebar width */
}

/* Style for router-link */
.nav-link {
  color: white;
}

.nav-link.active {
  background-color: #0d6efd !important;
}

.nav-link:not(.active):hover {
  background-color: #495057;
}
</style>
