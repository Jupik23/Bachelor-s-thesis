import 'bulma/css/bulma.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './styles/base.css'
import './styles/components.css'
import './styles/tokens.css'
import './styles/utilities.css'
import {createPinia} from 'pinia'
import { userAuthStore } from './lib/auth';

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.mount('#app')
const authStore = userAuthStore()
authStore.initializeAuth()