<template>
    <section class="section">
      <div class="container">
        <Card title="Login to your account">
          <form class="stack-4" @submit.prevent="onLoginViaJson">
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
        </Card>
      </div>
    </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../lib/api.js'
import Card from '@/components/Card.vue'
import { userAuthStore  } from '@/lib/auth'
const router = useRouter();
const route = useRoute();
const login = ref({email: '', password: ''})
const loading = ref(false)
const err = ref(null)
const authStore = userAuthStore()

const handleOAuthCallback = async () =>{
  const token = route.query.token;
  const error = route.query.error;
  if (error){
    console.error("OAuth error:", error);
    router.replace("/login")
    return;
  }
  if (token){
    console.log("OAuth is working");
    authStore.setToken(token);
    await authStore.checkToken();
    router.replace('/dashboard');
  }
}

async function onLoginViaJson() {
  loading.value = true
  err.value = null
  try{
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
    const {data} = await api.get('/api/v1/auth/facebook')
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

onMounted(() =>{
  handleOAuthCallback();
})
</script>
<style scoped>
.container{
  height: 80vh;
  display: flex;
  justify-content: center;
  align-items: center; 
}
</style>