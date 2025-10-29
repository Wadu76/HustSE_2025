<template>
  <div class="detail-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="book" class="book-detail">
      
      <div class="book-image-wrapper">
        <img v-if="book.images" :src="getImageUrl(book.images)" :alt="book.title" class="book-image" />
        <div v-else class="book-image-placeholder">无图片</div>
      </div>

      <div class="book-info">
        <h1>{{ book.title }}</h1>
        <p class="price">¥ {{ book.price }}</p>
        <p><strong>作者:</strong> {{ book.author || '未知' }}</p>
        <p><strong>新旧程度:</strong> {{ book.condition }}</p>
        <p><strong>课程标签:</strong> {{ book.course_tag }}</p>
        <p><strong>卖家ID:</strong> {{ book.seller_id }}</p>
        <p><strong>描述:</strong> {{ book.description || '暂无描述' }}</p>
        
        <button 
          @click="handleBuyNow" 
          :disabled="book.status !== 1"
          class="buy-button"
        >
          {{ book.status === 1 ? '立即购买' : '已售出' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// 【新增】导入 useRouter (用于跳转) 和 useUserStore (用于获取登录状态)
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/userStore'; //
import apiClient from '../api/api.js'; //

// 我们需要后端地址来拼接图片 URL
// (您的 apiClient 已配置 baseURL，所以我们可以用它)
const BACKEND_URL = apiClient.defaults.baseURL; // 'http://localhost:5000'

// --- 响应式变量 ---
const book = ref(null);
const loading = ref(false);
const error = ref(null);
const route = useRoute();
const router = useRouter(); // 【新增】
const userStore = useUserStore(); // 【新增】

// 3. 定义获取单本书籍的函数 (不变)
async function fetchBookDetail() {
  loading.value = true;
  error.value = null;
  const bookId = route.params.id; 
  
  try {
    const response = await apiClient.get(`/book/${bookId}`);
    book.value = response.data.data;
  } catch (err) {
    console.error('获取书籍详情失败:', err);
    if (err.response && err.response.status === 404) {
      error.value = '这本书不存在或已售出。';
    } else {
      error.value = '无法加载书籍详情，请稍后再试。';
    }
  } finally {
    loading.value = false;
  }
}

// 帮助函数：拼接图片 URL (不变)
function getImageUrl(imagePath) {
  if (!imagePath) return '';
  return `${BACKEND_URL}${imagePath}`;
}

// 6. 页面加载时 (onMounted)，执行获取函数 (不变)
onMounted(() => {
  fetchBookDetail();
});

// --- 【以下为新增的核心逻辑】 ---
// “立即购买”按钮的点击事件
const handleBuyNow = async () => {
  
  // 1. 检查是否登录 (从 Pinia Store 获取)
  if (!userStore.user) {
    alert('请先登录后再购买！');
    router.push('/login'); // 跳转到登录页
    return;
  }

  // 2. 检查是否在购买自己的书
  if (userStore.user.id === book.value.seller_id) {
    alert('不能购买自己发布的书籍！');
    return;
  }
  
  // 3. 确认购买
  if (!confirm(`您确定要以 ¥${book.value.price} 的价格购买《${book.value.title}》吗？`)) {
    return;
  }

  // 4. [核心] 调用创建订单 API
  try {
    const response = await apiClient.post('/order/create', {
      book_id: book.value.id // 传递 book_id 给后端
    });

    if (response.data.code === 200) {
      alert('订单创建成功！');
      
      // 5. 购买成功后，立即更新前端 UI
      book.value.status = 0; // 0 代表已售出 (与 book.py 对应)
      
      // 稍后开发完订单列表页后，可以跳转过去
      // router.push('/my-orders'); 
    } else {
      // 显示后端返回的错误，例如 "书籍不存在或已售出"
      alert(`购买失败: ${response.data.msg}`);
    }
  } catch (error) {
    console.error('创建订单失败:', error);
    if (error.response && error.response.data.msg) {
        alert(`创建订单时出错: ${error.response.data.msg}`);
    } else {
        alert('创建订单时发生网络错误');
    }
  }
};
</script>

<style scoped>
/* 您的 <style> 样式保持不变 */
/* ... (复制自您的 BookDetailView.vue) ... */
.detail-container {
  max-width: 900px;
  margin: 20px auto;
}
.book-detail {
  display: flex; 
  gap: 30px; 
}
.book-image-wrapper {
  flex: 1; 
}
.book-image {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.book-image-placeholder {
  width: 100%;
  height: 400px; 
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  color: #999;
  border-radius: 8px;
}
.book-info {
  flex: 2; 
}
.price {
  font-size: 2em;
  color: #e44d26; 
  font-weight: bold;
  margin: 10px 0;
}
.buy-button {
  padding: 12px 20px;
  font-size: 1.1em;
  background-color: #42b983; 
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.2s;
}
.buy-button:hover {
  background-color: #36a476; 
}
/* 【新增】禁用按钮的样式 */
.buy-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.loading, .error {
  font-size: 1.2em;
  color: #888;
}
.error {
  color: red;
}
</style>