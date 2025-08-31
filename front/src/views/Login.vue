<template>
  <BaseLayout>
    <section class="section">
      <div class="container">
        <div class="card auth-card">
          <form class="stack-4" @submit.prevent="onLoginViaJson">
            <h1>Sign in</h1>
            <input v-model="login.email" type="text" placeholder="Email" required>
            <input v-model="login.password" type="password" placeholder="Password" required>
            <button class="button" type="submit" :disabled="loading">
              {{  loading ? 'Logging in..':"Login" }}
            </button>
            <button class="facebook-button" type="button" :disabled="loading">
              <span class="icon"></span>
              <span class="buttonText"aria-label="Continue with Facebook">Facebook</span>
            </button>
            <p v-if="err" class="ta-center" style="color:var(--danger, #d33)">{{ error }}</p>
            <p class="ta-center">No account?
              <RouterLink to="/register">Create one</RouterLink>
            </p>
          </form>
        </div>
      </div>
    </section>
  </BaseLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseLayout from './Base.vue'
import api, { setAuthToken } from '../lib/api.js'

const router = useRouter()
const login = ref({email: '', password: ''})
const loading = ref(false)
const err = ref(null)

async function onLoginViaJson() {
  loading.value = true
  err.value = null
  try{
    const {data} = await api.post("/users/login" , {
      email: login.value.email,
      password: login.value.password
    }
  )
    const token = data?.access_token
    if(!token) throw new Error("No access token returned")
    setAuthToken(token)
    localStorage.setItem('token', token)
    router.push('/')
  }catch(e){
    err.value = e?.response?.data?.detail || e?.message || 'Registration failed. Please try again.'
  }finally{
    loading.value = false;
  }
}
</script>
<style>
.facebook-button{
  margin-left: 1%;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 46px;
  padding: 0 14px;
  background: linear-gradient(180deg, var(--primary), var(--primary-600));
  color:#fff; font-weight:700; letter-spacing:.01em;
  border-radius: 12px;
  border: 1px solid #1877F2;
  box-shadow: 0 1px 1px rgba(0,0,0,.25);
  white-space: nowrap;
  transition: filter .15s ease, transform .1s ease;
}
.facebook-button:hover{
  cursor: pointer;
  transform: translateY(-1px);
  filter:brightness(1.02); 
  transform:translateY(-1px); 
  box-shadow:0 10px 20px rgba(59,130,246,.28)
}
.facebook-button:active{
  transform: translateY(0)
}
.facebook-button .icon{
  width: 36px;
  height: 36px;
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  background-color: #1877F2; /* fallback blue behind the logo */
  background-image: url("../assets/2023_Facebook_icon.svg.png");
  background-size: 60% 60%;  /* keep the glyph nicely inset */
  background-position: center;
  background-repeat: no-repeat;
  flex: 0 0 36px;            /* prevent squeeze in flex layout */
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.2);
}
.facebook-button .buttonText{
  padding: 0;
  line-height: 1;
  font-weight: 600;
  color: inherit;
}
</style>