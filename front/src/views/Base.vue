<template>
  <div class="page">
    <header class="navbar">
      <div class="container navbar__inner">
        <RouterLink to="/" class="navbar__brand">Monitoring DietApp</RouterLink>
        <nav class="navbar__links" role="navigation" aria-label="Main">
          <RouterLink class="navbar__link" to="/about">About</RouterLink>
          <RouterLink class="navbar__link" to="/login">Login</RouterLink>
          <RouterLink class="navbar__link" to="/register">Register</RouterLink>
        </nav>
      </div>
    </header>

    <main class="main">
      <slot/>
    </main>

    <footer class="section">
      <div class="container ta-center muted">
        <small>&copy; {{ new Date().getFullYear() }} Monitoring DietApp</small>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.muted{ color: var(--muted); }
</style>