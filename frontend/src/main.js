import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { fetchCurrentUser } from './services/auth.js'

// Fetch user data on initial load if a token exists
fetchCurrentUser().then(() => {
  const app = createApp(App)

  app.use(router)

  app.mount('#app')
})

