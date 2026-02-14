import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ForceChangePasswordView from '../views/ForceChangePasswordView.vue'
import RequestPasswordResetView from '../views/RequestPasswordResetView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
// New views for the Personal Expense Manager
import ClientDashboardView from '../views/ClientDashboardView.vue' // Placeholder for client dashboard
import SuperadminClientsView from '../views/SuperadminClientsView.vue' // Placeholder for superadmin client management

import { accessToken } from '../services/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'client-dashboard',
      component: ClientDashboardView, // Placeholder for client dashboard
      meta: { requiresAuth: true, layout: 'DefaultLayout' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/force-change-password',
      name: 'force-change-password',
      component: ForceChangePasswordView,
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/request-password-reset',
      name: 'request-password-reset',
      component: RequestPasswordResetView,
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPasswordView,
      meta: { layout: 'LoginLayout' }
    },
    // Superadmin Routes
    {
      path: '/superadmin/login',
      name: 'superadmin-login',
      component: LoginView, // Reuse LoginView for superadmin login for now
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/superadmin/clients',
      name: 'superadmin-clients',
      component: SuperadminClientsView, // Placeholder for superadmin client management
      meta: { requiresAuth: true, layout: 'DefaultLayout' },
      beforeEnter: (to, from, next) => {
        // Ensure only superadmins can access this route
        // This will require fetching user data, which happens in App.vue and auth.js
        // For now, rely on backend auth, but later a client-side check can be added here
        if (accessToken.value) {
          next();
        } else {
          next('/superadmin/login');
        }
      }
    },
  ]
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth) && !accessToken.value) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router