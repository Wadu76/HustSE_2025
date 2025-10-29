// src/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'

// --- 【新增】 ---
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 导入 Element Plus 样式
// --- 【新增结束】 ---

import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)


app.use(ElementPlus) // 全局注册 Element Plus

app.mount('#app')