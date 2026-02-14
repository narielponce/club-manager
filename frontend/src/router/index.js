import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ClientDashboardView from '../views/ClientDashboardView.vue'
import ForceChangePasswordView from '../views/ForceChangePasswordView.vue'
import RequestPasswordResetView from '../views/RequestPasswordResetView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import SuperadminDashboardView from '../views/SuperadminDashboardView.vue'

import { accessToken } from '../services/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: ClientDashboardView,
      meta: { requiresAuth: true }
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
      component: LoginView,
      meta: { layout: 'LoginLayout' }
    },
    {
      path: '/superadmin/dashboard',
      name: 'superadmin-dashboard',
      component: SuperadminDashboardView,
      meta: { requiresAuth: true, isSuperadmin: true }
    },
  ]
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isSuperadminRoute = to.matched.some(record => record.meta.isSuperadmin)

  if (requiresAuth && !accessToken.value) {
    if (isSuperadminRoute) {
      next({ name: 'superadmin-login' })
    } else {
      next({ name: 'login' })
    }
  } else {
    next()
  }
})

export default router
