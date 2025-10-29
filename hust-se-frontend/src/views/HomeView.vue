<template>
  <div class="home-container">
    <h1>欢迎来到校园二手书平台</h1>
    <p>在售书籍列表：</p>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="books.length > 0" class="book-list">
      
      <!-- 
        --- 【核心修改】 ---
        1. 我们用 <router-link> 把 v-for 循环包起来
        2. :to="`/book/${book.id}`" 会生成 /book/1, /book/2 这样的动态链接
      -->
      <router-link 
        v-for="book in books" 
        :key="book.id" 
        :to="`/book/${book.id}`"
        class="book-card-link"
      >
        <!-- 
          我们把原来的 book-card 放在链接内部
        -->
        <div class="book-card">
          <img 
            v-if="book.images" 
            :src="getImageUrl(book.images)" 
            alt="Book cover" 
            class="book-image"
          />
          <div v-else class="book-image-placeholder">
            无图片
          </div>
          
          <h3>{{ book.title }}</h3>
          <p>价格: ¥ {{ book.price }}</p>
          <p>课程标签: {{ book.course_tag }}</p>
        </div>
      </router-link>
      <!-- 【修改结束】 -->

    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// 导入 apiClient 是为了获取 baseURL, 但 apiClient 本身没有导出 baseURL
// 我们直接在这里定义后端地址
const BACKEND_URL = 'http://localhost:5000';

import apiClient from '../api/api.js';

const books = ref([]);
const loading = ref(false);
const error = ref(null);

async function fetchBooks() {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/book/list');
    books.value = response.data.data.books;
    
    // F12 调试：看看后端返回的数据是否包含 images
    console.log('获取到的书籍:', books.value); 
    
  } catch (err) {
    console.error('获取书籍列表失败:', err);
    error.value = '无法加载书籍列表，请稍后再试。';
  } finally {
    loading.value = false;
  }
}

// 定义一个函数，把后端返回的相对路径 (/static/...)
// 和后端服务器地址拼接成一个完整的 URL
function getImageUrl(imagePath) {
  if (!imagePath) return '';
  // 返回: http://localhost:5000/static/uploads/my-pic.jpg
  return `${BACKEND_URL}${imagePath}`;
}

onMounted(() => {
  fetchBooks();
});
</script>

<style scoped>
.book-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* --- 【新增样式】 --- */
/* 我们需要重置 router-link 默认的 <a> 标签样式 
  (蓝色字体和下划线) 
*/
.book-card-link {
  text-decoration: none;
  color: inherit;
}
/* -------------------- */

.book-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 15px;
  width: 200px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  /* 【新增】添加一个悬停效果，让它看起来可点击 */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.book-image {
  width: 100%;
  height: 180px; /* 固定高度 */
  object-fit: cover; /* 保持图片比例，裁剪多余部分 */
  border-radius: 4px;
  margin-bottom: 10px;
}
.book-image-placeholder {
  width: 100%;
  height: 180px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  border-radius: 4px;
  margin-bottom: 10px;
}

.loading, .error {
  font-size: 1.2em;
  color: #888;
}
.error {
  color: red;
}
</style>