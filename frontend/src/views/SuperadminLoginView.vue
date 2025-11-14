<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card">
          <div class="card-header text-center">
            <h3>Superadmin Login</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" id="email" class="form-control" v-model="email" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" id="password" class="form-control" v-model="password" required>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Login</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login, fetchCurrentUser } from '../services/auth.js';
import { showSessionModal } from '../services/session.js';

const email = ref('');
const password = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const data = await login(email.value, password.value);
    if (data.access_token) {
      await fetchCurrentUser();
      router.push('/superadmin/dashboard');
    }
  } catch (err) {
    showSessionModal(
      "Error de Autenticación",
      "Usuario o contraseña incorrecto.",
      () => {} // Empty callback, just closes the modal
    );
    console.error(err);
  }
};
</script>
