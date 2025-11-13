<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from './layouts/DefaultLayout.vue'
import LoginLayout from './layouts/LoginLayout.vue'
import SessionExpiredModal from './components/SessionExpiredModal.vue'

const route = useRoute()

// A map of layout names to their components
const layouts = {
  DefaultLayout,
  LoginLayout
}

// A computed property to dynamically get the layout for the current route
const layoutComponent = computed(() => {
  // Default to DefaultLayout if no layout is specified
  return layouts[route.meta.layout] || DefaultLayout
})
</script>

<template>
  <component :is="layoutComponent">
    <router-view />
  </component>
  <SessionExpiredModal />
</template>

<style>
/* Global styles can go here, but it's better to use main.css */
</style>
