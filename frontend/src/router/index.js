import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ForceChangePasswordView from '../views/ForceChangePasswordView.vue'
import RequestPasswordResetView from '../views/RequestPasswordResetView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'

import { accessToken } from '../services/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
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