<template>
  <BaseLayout>
    <section class="section">
      <div class="container">
        <div class="card auth-card">
          <form class="stack-4" @submit.prevent="onRegister">
            <h1>Create account</h1>
            <input v-model="reg.name" type="text" placeholder="Name" required>
            <input v-model="reg.surname" type="text" placeholder="Surname" required>
            <input v-model="reg.username" type="text" placeholder="Username" required>
            <input v-model="reg.email" type="email" placeholder="Email address" required>
            <input v-model="reg.password" type="password" placeholder="Password (min 6)" minlength="6" required>
            <button class="button" type="submit">Create</button>
            <p class="ta-center">Already registered?
              <RouterLink to="/login">Sign in</RouterLink>
            </p>
          </form>
        </div>
      </div>
    </section>
  </BaseLayout>
</template>

<script setup>
import { ref } from 'vue'
import BaseLayout from './Base.vue'
const reg = ref({ name:'', surname:'', username:'', email:'', password:'' })
function onRegister(){ console.log('register', reg.value) }
</script>
