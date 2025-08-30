import 'bulma/css/bulma.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './styles/base.css'
import './styles/components.css'
import './styles/tokens.css'
import './styles/utilities.css'

createApp(App).use(router).mount('#app')
