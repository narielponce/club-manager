<template>
  <div>
    <!-- Vertical Sidebar (Visible on large screens) -->
    <div class="sidebar bg-dark text-white vh-100 p-3 d-none d-lg-flex flex-column">
      <div class="text-center">
        <img :src="logoSrc" alt="Logo" class="mb-3" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">
        <div v-if="currentUser" class="text-white text-truncate">
          <span v-if="currentUser.role === 'superadmin'" title="Panel de Superadministrador">
            Panel Superadmin
          </span>
          <span v-else-if="currentUser.club" :title="currentUser.club.name">
            {{ currentUser.club.name }}
          </span>
        </div>
      </div>
      <hr>
      <ul class="nav nav-pills flex-column mb-auto">
        <li v-if="canViewMembers" class="nav-item">
          <router-link to="/" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-people-fill me-2" viewBox="0 0 16 16">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1H7zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
              <path fill-rule="evenodd" d="M5.216 14A2.238 2.238 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.325 6.325 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1h4.216zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/>
            </svg>
            Socios
          </router-link>
        </li>
        <li v-if="canManageFinances" class="nav-item">
          <router-link to="/finances" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-currency-dollar me-2" viewBox="0 0 16 16">
              <path d="M4 10.781c.148.14.386.293.74.46.658.307 1.573.629 2.52.876.543.148 1.07.288 1.555.404h.003a8.329 8.329 0 0 1 .584.122 25.157 25.157 0 0 1 .585.122c.22.046.45.085.695.119L12 11.76V10.31a11.275 11.275 0 0 0-.468-.095 23.653 23.653 0 0 0-.612-.124l-.004-.001a12.904 12.904 0 0 0-.585-.123 25.157 25.157 0 0 0-.585-.122c-.22-.046-.45-.085-.695-.119L4 10.31v.471zm0-1.766V7.403c.46-.084.95-.171 1.446-.272l.004-.001c.27-.057.54-.11.81-.162.269-.053.539-.103.809-.149.23-.04.45-.073.67-.101L12 6.35V4.905a11.275 11.275 0 0 0-.468-.095 23.653 23.653 0 0 0-.612-.124L10.31 4.78c-.27-.057-.54-.11-.81-.162-.269-.053-.539-.103-.809-.149-.23-.04-.45-.073-.67-.101L4 4.905v.471zm-1-4.905h.003L5.85 3.496a.5.5 0 0 1-.316-.923L2.5 3.084V2.5a.5.5 0 0 1 1 0v.584zm11 0a.5.5 0 0 1 1 0v.584l-3.034-.923a.5.5 0 0 1-.316.923L12.5 3.496h.003V2.5a.5.5 0 0 1 1 0v.584zM12 1.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zm-11 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zM12 14.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zm-11 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5z"/>
            </svg>
            Finanzas
          </router-link>
        </li>
        <li v-if="canManageFinances" class="nav-item">
          <a class="nav-link text-white d-flex align-items-center" data-bs-toggle="collapse" href="#reports-submenu" role="button" aria-expanded="false" aria-controls="reports-submenu">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-bar-chart-line-fill me-2" viewBox="0 0 16 16">
              <path d="M11 2a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v12h.5a.5.5 0 0 1 0 1H.5a.5.5 0 0 1 0-1H1v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h1V7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7h1V2z"/>
            </svg>
            Informes
          </a>
          <div class="collapse" id="reports-submenu">
            <ul class="nav flex-column ms-4">
              <li class="nav-item">
                <router-link to="/reports" class="nav-link text-white py-1" active-class="active">Ingresos por Actividad</router-link>
              </li>
              <!-- Future report links can be added here -->
            </ul>
          </div>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/activities" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-calendar-check me-2" viewBox="0 0 16 16">
              <path d="M10.854 7.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 9.793l2.646-2.647a.5.5 0 0 1 .708 0z"/>
              <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
            </svg>
            Actividades
          </router-link>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/users" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-person-fill-gear me-2" viewBox="0 0 16 16">
              <path d="M11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm-9 8c0 1 1 1 1 1h5.256A4.493 4.493 0 0 1 8 12.5a4.49 4.49 0 0 1 1.544-3.393C7.077 9.038 6 8.5 6 8c0-1 1-1 1-1h.256A4.5 4.5 0 0 1 8 5.5a4.5 4.5 0 0 1 1.544 3.393c.81-.42 1.55-.936 2.207-1.554C11.442 6.32 10.27 6 9 6c-2 0-4 1-4 2 0 .5.224 1.342 1.256 2.393Z"/>
              <path d="M16 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-3.5-2a.5.5 0 0 0-.5.5v1h-1a.5.5 0 0 0 0 1h1v1a.5.5 0 0 0 1 0v-1h1a.5.5 0 0 0 0-1h-1v-1a.5.5 0 0 0-.5-.5Z"/>
            </svg>
            Usuarios
          </router-link>
        </li>
        <li v-if="isAdmin" class="nav-item">
          <router-link to="/settings" class="nav-link text-white d-flex align-items-center" active-class="active">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-gear-fill me-2" viewBox="0 0 16 16">
              <path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311a1.464 1.464 0 0 1-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413-1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.858 2.929 2.929 0 0 1 0 5.858z"/>
            </svg>
            Configuración
          </router-link>
        </li>
      </ul>
      <hr>
      <div v-if="currentUser">
        <a href="#" @click.prevent="logout" class="nav-link text-white d-flex align-items-center mt-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-box-arrow-right me-2" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0v2z"/>
            <path fill-rule="evenodd" d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3z"/>
          </svg>
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

const defaultLogo = "data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='30' fill='%23495057'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='24' font-family='sans-serif' dy='.1em'%3ECM%3C/text%3E%3C/svg%3E";

const logoSrc = computed(() => {
  if (currentUser.value?.club?.logo_url) {
    return `/${currentUser.value.club.logo_url}`;
  }
  return defaultLogo;
});

const isAdmin = computed(() => currentUser.value?.role === 'admin')
const canViewMembers = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'tesorero' || role === 'profesor'
})
const canManageFinances = computed(() => {
  const role = currentUser.value?.role
  return role === 'admin' || role === 'tesorero' // Assuming tesorero can also see finances
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
