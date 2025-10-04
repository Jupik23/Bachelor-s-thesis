<template>
    <section class="section">
      <div class="container">
        <div class="auth-card">
          <form class="stack-4" @submit.prevent="onLoginViaJson">
            <h1>Sign in</h1>
            <input v-model="login.email" type="text" placeholder="Email" required>
            <input v-model="login.password" type="password" placeholder="Password" required>
            <button class="btn" type="submit" :disabled="loading">
              {{  loading ? 'Logging in..':"Login" }}
            </button>
            <button class="facebook-button" type="button" :disabled="loading" @click="loginViaFacebook">
              <span class="icon"></span>
              <span class="buttonText"aria-label="Continue with Facebook">Facebook</span>
            </button>
            <p v-if="err" class="ta-center" style="color:var(--danger, #d33)">{{ err }}</p>
            <p class="ta-center">No account?
              <RouterLink to="/register">Create one</RouterLink>
            </p>
          </form>
        </div>
      </div>
    </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { setAuthToken } from '../lib/api.js'
import { userAuthStore } from '@/lib/auth'
const router = useRouter()
const login = ref({email: '', password: ''})
const loading = ref(false)
const err = ref(null)

async function onLoginViaJson() {
  loading.value = true
  err.value = null
  try{
    const authStore = userAuthStore()
    const res = await authStore.login({
      email: login.value.email,
      password: login.value.password
    })
    if(res.success){
      router.push("/dashboard")
    }else{
      err.value = res.error
    }
  }catch(e){
    err.value = "Login failed"
  }finally{
    loading.value = false
  }
}

async function loginViaFacebook() {
  loading.value = true
  err.value = null
  try{
    const {data} = await api.get('/api/v1/fauth/facebook')
    if(!data?.authorization_url){
      throw new Error("No authorization received")
    }
    if(data.state){
      sessionStorage.setItem('oauth_state', data.state)
    }
    window.location.href = data.authorization_url
  }catch(e){
    err.value = e?.response?.data?.detail || e?.message || 'Login via Facebook failed. Please try again.'
  }finally{
    loading.value = false;
  }
}

async function handleOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  const storedState = sessionStorage.getItem('oauth_state')
  loading.value = true
  err.value = null

  if (state !== storedState){
    throw new Error("Invalid state")
  }
  const {data} = await api.post("api/v1/auth/facebook/callback")
}
</script>
<style scoped>
.section{
  min-height: 100vh;
  width: 100%;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.container{
}
.btn{

}
.auth-card{
  padding: 30px;
}
</style>