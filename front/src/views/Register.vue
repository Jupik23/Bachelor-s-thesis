<template>
  <section class="section">
    <div class="container">
      <div class="card auth-card">
        <form class="stack-4" @submit.prevent="onRegister">
          <h1>Create account</h1>
          <input v-model="reg.name" type="text" placeholder="Name" 
            autocomplete="given-name"  required>
          <input v-model="reg.surname" type="text" placeholder="Surname"
            autocomplete="family-name" required>
          <input v-model="reg.username" type="text" placeholder="Username"
            autocomplete="username" required>
          <input v-model="reg.email" type="email" placeholder="Email address"
            autocomplete="email" required>
          <input v-model="reg.password" type="password" placeholder="Password (min 6)"
              minlength="6" required>
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Creating…' : 'Create' }}
          </button>
          <p v-if="err" class="ta-center" style="color:var(--danger,#d33)">{{ err }}</p>
          <p class="ta-center">Already registered?
            <RouterLink to="/login">Sign in</RouterLink>
          </p>
        </form>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import api from "../lib/api.js"
import { useRouter } from 'vue-router'

const reg = ref({ name:'', surname:'', username:'', email:'', password:'' })
const loading = ref(false)
const err = ref(null)
const router = useRouter()

function validateRegisterForm(){
  if (!reg.value.name || !reg.value.surname || !reg.value.username 
    || !reg.value.email || !reg.value.password
  ) {
    err.value = "Fill in all fields"
    return false
  }
  if (reg.value.password.length < 6){
    err.value = "Password must be at least 6 characters."
    return false
  }
  return true
}

async function onRegister() {
  if (loading.value) return
  if (!validateRegisterForm()) return

  loading.value = true
  err.value = null
  try{
    await api.post("/api/v1/users/", {
      user_data:{
        name: reg.value.name,
        surname: reg.value.surname,
        login: reg.value.username,
      },
      user_auth_data:{
        email: reg.value.email,
        password: reg.value.password,
      }
  })
    await router.push("/login")
  }catch(e){
    err.value = e?.response?.data?.detail || e?.message || 'Registration failed. Please try again.'
  }finally{
    loading.value = false;
  }
};
</script>
