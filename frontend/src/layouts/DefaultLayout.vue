<template>
  <div>
    <!-- Vertical Sidebar (Visible on large screens) -->
    <div class="sidebar bg-dark text-white vh-100 p-3 d-none d-lg-flex flex-column">
      <a href="/" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
        <span v-if="currentUser" class="fs-4">{{ currentUser.club.name }}</span>
        <span v-else class="fs-4">Club Manager</span>
      </a>
      <hr>
      <ul class="nav nav-pills flex-column mb-auto">
        <li v-if="canViewMembers" class="nav-item">
          <router-link to="/" class="nav-link text-white" active-class="active">Socios</router-link>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/activities" class="nav-link text-white" active-class="active">Actividades</router-link>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/users" class="nav-link text-white" active-class="active">Usuarios</router-link>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/settings" class="nav-link text-white" active-class="active">Configuración</router-link>
        </li>
      </ul>
      <hr>
      <div v-if="currentUser">
        <!--<div class="text-white small">{{ currentUser.email }}</div>-->
        <a href="#" @click.prevent="logout" class="nav-link text-white d-block mt-1">
          Logout
        </a>
      </div>
    </div>

    <!-- Content Wrapper -->
    <div class="content-wrapper">
      <!-- Topbar (becomes collapsible on small screens) -->
      <nav class="navbar navbar-expand-lg navbar-light bg-white topbar static-top shadow">
        <div class="container-fluid">
          <!-- Hamburger Toggler (Visible on small screens) -->
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbarCollapse"
            aria-controls="mainNavbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>

          <!-- Collapsible wrapper -->
          <div class="collapse navbar-collapse" id="mainNavbarCollapse">
            <!-- Mobile Nav Links -->
            <ul class="navbar-nav mb-2 mb-lg-0">
              <li v-if="canViewMembers" class="nav-item d-lg-none">
                <router-link to="/" class="nav-link" active-class="active">Socios</router-link>
              </li>
              <li v-if="isAdmin" class="nav-item d-lg-none">
                <router-link to="/activities" class="nav-link" active-class="active">Actividades</router-link>
              </li>
              <li v-if="isAdmin" class="nav-item d-lg-none">
                <router-link to="/users" class="nav-link" active-class="active">Usuarios</router-link>
              </li>
              <li v-if="isAdmin" class="nav-item d-lg-none">
                <router-link to="/settings" class="nav-link" active-class="active">Configuración</router-link>
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

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const canViewMembers = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'tesorero' || role === 'profesor'
})
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
</style>
