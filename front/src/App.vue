<script setup>
import Base from "./views/Base.vue";
import Home from "./views/Home.vue";
import Nav from "./components/partial/Nav.vue"
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
