<script setup>
import Navbar from './components/layout/Navbar.vue';
import Footer from './components/layout/Footer.vue';
</script>

<template>
  <div class="app">
    <Navbar/>
    <router-view />
    <Footer/>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
