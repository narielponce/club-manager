import { createRouter, createWebHistory } from 'vue-router'
import MembersView from '../views/MembersView.vue'
import LoginView from '../views/LoginView.vue'
import UsersView from '../views/UsersView.vue'
import ActivitiesView from '../views/ActivitiesView.vue'
import SettingsView from '../views/SettingsView.vue'
import DebtView from '../views/DebtView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { layout: 'LoginLayout' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: MembersView,
    meta: { requiresAuth: true } // This route will require authentication
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: { requiresAuth: true }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: ActivitiesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/debts',
    name: 'Debts',
    component: DebtView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
