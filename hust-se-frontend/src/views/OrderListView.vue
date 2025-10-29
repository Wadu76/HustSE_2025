<template>
  <div class="order-list-container">
    <h2>我的订单</h2>

    <div v-if="!userStore.user">
      <p>请先 <router-link to="/login">登录</router-link> 查看您的订单。</p>
    </div>

    <div v-else>
      <div class="filter-buttons">
        <button @click="fetchOrders('buyer')" :class="{ active: currentRole === 'buyer' }">
          我买的 (Buyer)
        </button>
        <button @click="fetchOrders('seller')" :class="{ active: currentRole === 'seller' }">
          我卖的 (Seller)
        </button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      
      <div v-else-if="orders.length === 0" class="empty">
        暂无订单。
      </div>

      <div v-else class="order-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <h3>订单号: {{ order.order_no }}</h3>
          <p><strong>书籍:</strong> {{ order.book_title }}</p>
          <p><strong>价格:</strong> ¥ {{ order.price }}</p>
          <p><strong>状态:</strong> <span class="status">{{ order.status_text }}</span></p>
          <p v-if="currentRole === 'buyer'">
            <strong>卖家:</strong> {{ order.seller_name }}
          </p>
          <p v-if="currentRole === 'seller'">
            <strong>买家:</strong> {{ order.buyer_name }}
          </p>
          <p class="time">创建时间: {{ order.create_time }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore'; // 1. 导入用户 store

const orders = ref([]);
const loading = ref(false);
const error = ref(null);
const currentRole = ref('buyer'); // 默认显示“我买的”
const userStore = useUserStore(); // 2. 获取 store 实例

// 3. 定义获取订单的函数
async function fetchOrders(role = 'buyer') {
  // 检查是否登录
  if (!userStore.user) {
    error.value = '请先登录。';
    return;
  }

  loading.value = true;
  error.value = null;
  currentRole.value = role; // 更新当前角色

  try {
    // 4. 调用后端的 /order/list 接口，并传入 role 参数
    const response = await apiClient.get('/order/list', {
      params: {
        role: role // 'buyer' 或 'seller'
      }
    });
    
    // 5. 将返回的订单数据存入 ref
    if (response.data.code === 200) {
      orders.value = response.data.data.orders;
    } else {
      error.value = response.data.msg;
    }
  } catch (err) {
    console.error(`获取订单列表 (role=${role}) 失败:`, err);
    if (err.response && err.response.status === 401) {
      error.value = '请先登录后再查看订单。';
    } else {
      error.value = '无法加载订单列表，请稍后再试。';
    }
  } finally {
    loading.value = false;
  }
}

// 6. 页面加载时 (onMounted)，默认获取买家订单
onMounted(() => {
  fetchOrders('buyer');
});
</script>

<style scoped>
.order-list-container {
  max-width: 800px;
  margin: 20px auto;
}

.filter-buttons {
  margin-bottom: 20px;
}
.filter-buttons button {
  padding: 8px 15px;
  margin-right: 10px;
  border: 1px solid #ccc;
  background-color: #f0f0f0;
  cursor: pointer;
}
.filter-buttons button.active {
  background-color: #42b983;
  color: white;
  border-color: #42b983;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.order-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.order-card h3 {
  margin-top: 0;
  font-size: 1.1em;
}
.status {
  font-weight: bold;
  color: #e44d26;
}
.time {
  font-size: 0.9em;
  color: #888;
}

.loading, .error, .empty {
  font-size: 1.1em;
  color: #888;
  text-align: center;
  padding: 20px;
}
.error {
  color: red;
}
</style>