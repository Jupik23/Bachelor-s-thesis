<script setup>
import Base from "./layouts/Base.vue";
import Home from "./views/Home.vue";
import Nav from "./components/partial/Sidebar.vue"
</script>

<template>
  <router-view />
  <div class="app">
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
