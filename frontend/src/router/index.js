import { createRouter, createWebHistory } from 'vue-router'
import MembersView from '../views/MembersView.vue'
import LoginView from '../views/LoginView.vue'
import ActivitiesView from '../views/ActivitiesView.vue'
import UsersView from '../views/UsersView.vue'
import SettingsView from '../views/SettingsView.vue'
import SuperadminLoginView from '../views/SuperadminLoginView.vue'
import CreateClubView from '../views/CreateClubView.vue'
import SuperadminDashboardView from '../views/SuperadminDashboardView.vue'
import FinancesView from '../views/FinancesView.vue'
import { token } from '../services/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'members',
      component: MembersView,
      meta: { requiresAuth: true }
    },
    {
      path: '/activities',
      name: 'activities',
      component: ActivitiesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView,
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/finances',
      name: 'finances',
      component: FinancesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { layout: 'LoginLayout' }
    },
    // Superadmin Routes
    {
      path: '/superadmin/login',
      name: 'superadmin-login',
      component: SuperadminLoginView,
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/superadmin/dashboard',
      name: 'superadmin-dashboard',
      component: SuperadminDashboardView,
      meta: { requiresAuth: true }, // Use the main app layout
      beforeEnter: (to, from, next) => {
        if (token.value) {
          next();
        } else {
          next('/superadmin/login');
        }
      }
    },
    {
      path: '/superadmin/create-club',
      name: 'create-club',
      component: CreateClubView,
      meta: { requiresAuth: true }, // Use the main app layout
      beforeEnter: (to, from, next) => {
        if (token.value) {
          next();
        } else {
          next('/superadmin/login');
        }
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth) && !token.value) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
