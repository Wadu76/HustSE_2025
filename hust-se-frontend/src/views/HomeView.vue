<template>
  <div class="home-container">
    <el-page-header title="返回" content="在售书籍列表" @back="onBack" />

    <div v-if="loading" v-loading.fullscreen.lock="loading" element-loading-text="正在拼命加载中..."></div>
    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />

    <el-row v-if="books.length > 0" :gutter="20" class="book-list">
      
      <el-col
        v-for="book in books" 
        :key="book.id" 
        :xs="24" :sm="12" :md="8" :lg="6" :xl="4"
      >
        <el-card shadow="hover" :body-style="{ padding: '0px' }" class="book-card">
          
          <router-link :to="`/book/${book.id}`" class="book-card-link">
            
            <el-image :src="getImageUrl(book.images)" lazy class="book-image">
              <template #placeholder>
                <div class="image-placeholder">加载中...</div>
              </template>
              <template #error>
                <div class="image-placeholder">无图片</div>
              </template>
            </el-image>

            <div class="book-info">
              <h3>{{ book.title }}</h3>
              <p class="price">¥ {{ book.price }}</p>
              <p class="tag">
                <el-tag size="small">{{ book.course_tag }}</el-tag>
              </p>
            </div>
            
          </router-link>
        </el-card>
      </el-col>
    </el-row>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/api.js';
import { ElMessage } from 'element-plus'; // 导入消息提示

// 【修改】我们应该使用 apiClient 实例上配置的 baseURL
const BACKEND_URL = apiClient.defaults.baseURL; 

const books = ref([]);
const loading = ref(false);
const error = ref(null);

async function fetchBooks() {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/book/list');
    books.value = response.data.data.books;
  } catch (err) {
    console.error('获取书籍列表失败:', err);
    error.value = '无法加载书籍列表，请稍后再试。';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
}

// 拼接图片 URL
function getImageUrl(imagePath) {
  if (!imagePath) return '';
  // 【修改】确保 BACKEND_URL 被正确使用
  return `${BACKEND_URL}${imagePath}`;
}

onMounted(() => {
  fetchBooks();
});

// el-page-header 的返回按钮事件
const onBack = () => {
  ElMessage.info('已经在首页了');
}
</script>

<style scoped>
/* 旧的 .book-list, .book-card 等样式 已被 Element Plus 取代
  我们只需要添加少量自定义样式
*/
.el-page-header {
  margin-bottom: 20px;
}

.book-list {
  margin-top: 20px;
}

.book-card {
  margin-bottom: 20px; /* 卡片之间的垂直间距 */
}

/* 重置 router-link 样式 */
.book-card-link {
  text-decoration: none;
  color: inherit;
}

.book-image {
  width: 100%;
  height: 250px; /* 固定高度，el-image 会自动处理 object-fit */
  display: block; /* 移除图片底部的额外空间 */
}

/* el-image 的占位符样式 */
.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 250px;
  background-color: #f5f7fa;
  color: #c0c4cc;
}

.book-info {
  padding: 15px;
}
.book-info h3 {
  font-size: 1.1em;
  margin: 0 0 10px 0;
  /* 限制标题只显示一行，多余显示省略号 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.book-info p {
  margin: 0;
  font-size: 0.9em;
}
.price {
  font-size: 1.2em;
  font-weight: bold;
  color: #e44d26;
  margin-bottom: 10px;
}
.tag {
  color: #888;
}
</style>