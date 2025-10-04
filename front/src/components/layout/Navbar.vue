<script setup>
import { userAuthStore } from '@/lib/auth';
import { RouterLink } from 'vue-router';
const authStore = userAuthStore();
</script>

<template>
    <nav class="navbar">   
        <div>
            <RouterLink to="/">
                <img src="@\assets\images\small-logo.png" class="navbar-logo"></img>
            </RouterLink>
            <ul class="nav-menu">
                <li><RouterLink to="/features" class="nav-link">Features</RouterLink></li>
                <li><RouterLink to="/dashboard" class="nav-link">Dashboard</RouterLink></li>
                <li><RouterLink to="/about" class="nav-link">About</RouterLink></li>
            </ul>
            <div class="login-logout">
                <template v-if="!authStore.isLoggedIn">
                    <RouterLink to="/login">Sign In</RouterLink>
                    <RouterLink to="/register">Get Started</RouterLink>
                </template>
                <template v-else>
                    <RouterLink to="/dashboard">Profile</RouterLink>
                    <RouterLink to="/login" @click="authStore.logout">Logout</RouterLink>
                </template>
            </div>
            

        </div>
    </nav>
</template>

<style scoped>
.navbar{
    background-color: var(--white-color);
    padding: 1rem 2rem;
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: 1000;
}
.navbar > div{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 auto;
    gap: 5rem;
    max-width: 1200px;
}
.navbar-logo{
    flex-shrink: 0;
    max-height: 50px;
    max-width: 50px;
}
.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
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
.login-logout{
    display: flex;
    gap: 1rem;
}
</style>