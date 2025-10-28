// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 导入 Pinia
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia() // 2. 创建 Pinia 实例

app.use(pinia) // 3. 告诉 Vue 应用使用 Pinia
app.mount('#app')