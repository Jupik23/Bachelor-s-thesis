<script setup>
import Navbar from './components/layout/Navbar.vue';
import Footer from './components/layout/Footer.vue';
import "@/assets/styles/main.css"
</script>

<template>
  <div class="app">
    <Navbar/>
    <main class="main-content">
      <router-view />
    </main>
    <Footer/>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content{
  flex-grow: 1;
}
</style>
