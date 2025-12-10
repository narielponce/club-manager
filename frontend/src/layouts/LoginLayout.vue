<template>
  <div class="login-layout d-flex align-items-center justify-content-center">
    <slot />
  </div>
</template>

<style scoped>
.login-layout {
  min-height: 100vh;
  background-image: url('/fondo-login-3.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
</style>
