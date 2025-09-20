<template>
  <header class="navbar">
    <div class="container navbar__inner">
      <RouterLink to="/" class="navbar__brand">WellPlan</RouterLink>
      <nav class="navbar__links" role="navigation" aria-label="Main">
        <RouterLink class="navbar__link" to="/about">About</RouterLink>
        <template v-if="userAuthStore.isLoggedIn">
          <RouterLink class="navbar__link" to="dashboard">Dashboard</RouterLink>
          <button class="navbar__link button--logout" @click="handleLogout">
            Logout
          </button>
        </template>
        <tempale v-else>
          <RouterLink class="navbar__link" to="/login">Login</RouterLink>
          <RouterLink class="navbar__link" to="/register">Register</RouterLink>
        </tempale>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { userAuthStore } from '@/lib/auth';
import { RouterLink } from 'vue-router'
</script>
