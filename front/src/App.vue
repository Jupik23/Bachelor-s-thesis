<script setup>
import Navbar from './components/layout/Navbar.vue';
</script>

<template>
  <div class="app">
    <Navbar/>
    <router-view />
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
