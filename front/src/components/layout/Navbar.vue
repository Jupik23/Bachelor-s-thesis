<script setup lang="ts">
import { userAuthStore } from '@/lib/auth';
import { RouterLink } from 'vue-router';

</script>

<template>
    <nav class="navbar">   
        <div>
            <RouterLink to="/" class="navbar-logo">
                <img src=""></img>
            </RouterLink>
            <ul class="nav-menu">
                <li><RouterLink to="/features" class="nav-link">Features</RouterLink></li>
                <li><RouterLink to="/dashboard" class="nav-link">Dashboard</RouterLink></li>
                <li><RouterLink to="/about" class="nav-link">About</RouterLink></li>
            </ul>
            <div class="login-logout">
                <template v-if="!userAuthStore.isLoggedIn">
                    <RouterLink to="/login">Sign In</RouterLink>
                    <RouterLink to="/register">Get Started</RouterLink>
                </template>
                <template v-else>
                    <RouterLink to="/dashboard">Profile</RouterLink>
                    <button @click="userAuthStore.Logout()">Logout</button>
                </template>
            </div>
            

        </div>
    </nav>
</template>

<style scoped>
.navbar{
    background-color: #ffff;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    position: sticky;
    top: 0;
}
.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1.5rem;
}
.nav-link {
  display: inline-block;
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.3s ease;
}
.nav-link:hover{
    color: #27ae60; 
    transform: scale(1.2);
}
</style>