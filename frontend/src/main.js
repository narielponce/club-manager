import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { fetchCurrentUser } from './services/auth.js'

// Fetch user data on initial load if a token exists
fetchCurrentUser().then(() => {
  const app = createApp(App)
  
  // Define global utility functions
  app.config.globalProperties.$formatCurrency = (value) => {
    if (value === null || value === undefined) return '';
    return new Intl.NumberFormat('es-ES', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };
  
  app.use(router)
  
  app.mount('#app')})

