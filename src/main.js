import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import lazyplugin from 'vue3-lazy'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(lazyplugin, {
    loading: 'loading.png',
    error: 'loading.png'
})

app.mount('#app')
