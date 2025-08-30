<!-- src/components/NavBar.vue (if you want it separate; BaseLayout already includes a navbar) -->
<template>
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
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
