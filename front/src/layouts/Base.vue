<template>
  <div class="page">
    <header class="navbar">
      <div class="container navbar__inner">
        <button v-if="authStore.isLoggedIn"
        @click="toggleSidebar",
        aria-label="Toggle Navigation">
          =
        </button>
        <RouterLink to="/" class="navbar__brand">WellPlan</RouterLink>
        <nav class="navbar__links" role="navigation" aria-label="Main">
          <RouterLink class="navbar__link" to="/about">About</RouterLink>
          <template v-if="!authStore.isLoggedIn">
            <RouterLink class="navbar__link" to="/login">Login</RouterLink>
            <RouterLink class="navbar__link" to="/register">Register</RouterLink>
          </template>
        </nav>
      </div>
    </header>
    <Sidebar v-if="authStore.isLoggedIn" :isVisible="isSidebarVisible" @close="isSidebarVisible = false"/>
    <div v-if="isSidebarVisible" class="overlay" @click="isSidebarVisible = false"></div>

    <main class="main">
      <slot></slot>
    </main>

    <footer class="section">
      <div class="container ta-center muted">
        <small>&copy; {{ new Date().getFullYear() }} WellPla123123n</small>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import Sidebar from '@/components/partial/Sidebar.vue'
import { userAuthStore } from '@/lib/auth';
import { ref } from 'vue'
const authStore = userAuthStore()
const isSidebarVisible = ref(false)
const toggleSidebar = () => {
  isSidebarVisible.value = !isSidebarVisible.value
}
</script>

<style scoped>
.muted{ color: var(--muted); }
</style>