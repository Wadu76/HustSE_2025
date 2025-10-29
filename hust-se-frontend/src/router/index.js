// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
// ... (HomeView, LoginView, RegisterView, CreateBookView, BookDetailView, OrderListView)
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import CreateBookView from '../views/CreateBookView.vue';
import BookDetailView from '../views/BookDetailView.vue';
import OrderListView from '../views/OrderListView.vue';

// --- 【新增】 1. 导入我们刚创建的资料页 ---
import ProfileView from '../views/ProfileView.vue';

const routes = [
    // ... (/, /login, /register, /create-book, /orders)
    { path: '/', name: 'Home', component: HomeView },
    { path: '/login', name: 'Login', component: LoginView },
    { path: '/register', name: 'Register', component: RegisterView },
    { path: '/create-book', name: 'CreateBook', component: CreateBookView },
    { path: '/orders', name: 'OrderList', component: OrderListView },

    // --- 【新增】 2. 添加路由配置 ---
    {
        path: '/profile', // 访问 /profile 时
        name: 'Profile',
        component: ProfileView // 显示 ProfileView 组件
    },
    // --- 【以上为新增】 ---

    {
        path: '/book/:id',
        name: 'BookDetail',
        component: BookDetailView
    }
];

// ... (router 创建部分不变) ...
const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;