import { createApp } from 'vue'
import App from './App.vue'
import router from '@/router'
import pinia from '@/stores'
import installElement from '@/plugins/element'

import '@/assets/styles/global.css'
import '@/assets/styles/cosmic-theme.css'

const app = createApp(App)
app.use(pinia)
app.use(router)
installElement(app)
app.mount('#app')
