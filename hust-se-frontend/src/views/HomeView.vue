<template>
  <div class="home-container">
    
    <el-card class="search-filter-card">
      <el-form :model="searchParams" :inline="true" @submit.prevent="handleSearch">
        
        <el-form-item label="书名搜索:">
          <el-input 
            v-model="searchParams.search" 
            placeholder="搜索书名..." 
            clearable
          />
        </el-form-item>
        
        <el-form-item label="课程标签:">
          <el-input 
            v-model="searchParams.course_tag" 
            placeholder="例如：软件工程" 
            clearable
          />
        </el-form-item>

        <el-form-item label="价格区间:">
          <el-input-number 
            v-model="searchParams.min_price"
            :min="0"
            :precision="2"
            controls-position="right"
            placeholder="最低价"
            style="width: 120px;"
          />
          <span style="margin: 0 5px;">-</span>
          <el-input-number 
            v-model="searchParams.max_price"
            :min="0"
            :precision="2"
            controls-position="right"
            placeholder="最高价"
            style="width: 120px;"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><SearchIcon /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            重置
          </el-button>
        </el-form-item>

      </el-form>
    </el-card>
    <div v-if="loading" v-loading.fullscreen.lock="loading" element-loading-text="正在拼命加载中..."></div>
    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
    <el-alert v-if="!loading && books.length === 0" title="没有找到符合条件的书籍" type="info" show-icon :closable="false" />

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
// 【修改】导入 reactive 和图标
import { ref, onMounted, reactive } from 'vue'; 
import apiClient from '../api/api.js';
import { ElMessage } from 'element-plus';
import { Search as SearchIcon } from '@element-plus/icons-vue'; // 导入搜索图标

const BACKEND_URL = apiClient.defaults.baseURL; 

const books = ref([]);
const loading = ref(false);
const error = ref(null);

// --- 【新增】 1. 存储搜索/筛选条件的响应式对象 ---
const searchParams = reactive({
  search: '',       // 对应后端的 'search'
  course_tag: '',   // 对应后端的 'course_tag'
  min_price: null,  // 对应后端的 'min_price'
  max_price: null   // 对应后端的 'max_price'
});
// --- 【新增结束】 ---

// --- 【修改】 2. 更新 fetchBooks 函数以发送参数 ---
async function fetchBooks() {
  loading.value = true;
  error.value = null;
  
  // 2.1 准备要发送的参数
  const params = {};
  if (searchParams.search) {
    params.search = searchParams.search;
  }
  if (searchParams.course_tag) {
    params.course_tag = searchParams.course_tag;
  }
  if (searchParams.min_price) {
    params.min_price = searchParams.min_price;
  }
  if (searchParams.max_price) {
    params.max_price = searchParams.max_price;
  }

  try {
    // 2.2 将参数附加到 GET 请求
    const response = await apiClient.get('/book/list', { 
      params: params // { params: { search: 'Java', course_tag: 'CS' } }
    });
    books.value = response.data.data.books;
  } catch (err) {
    console.error('获取书籍列表失败:', err);
    error.value = '无法加载书籍列表，请稍后再试。';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
}
// --- 【修改结束】 ---

// (getImageUrl 函数不变)
function getImageUrl(imagePath) {
  if (!imagePath) return '';
  return `${BACKEND_URL}${imagePath}`;
}

onMounted(() => {
  fetchBooks();
});

// --- 【新增】 3. 搜索和重置函数 ---
function handleSearch() {
  // 只需调用 fetchBooks，它会读取 searchParams 的最新值
  fetchBooks();
}

function resetSearch() {
  // 重置所有搜索条件
  searchParams.search = '';
  searchParams.course_tag = '';
  searchParams.min_price = null;
  searchParams.max_price = null;
  // 重新获取所有书籍
  fetchBooks();
}
// --- 【新增结束】 ---

</script>

<style scoped>
/* --- 【新增】搜索卡片的样式 --- */
.search-filter-card {
  margin-bottom: 20px;
}
/* --- 【新增结束】 --- */

/* (el-page-header 的样式被移除了) */

.book-list {
  margin-top: 20px;
}
/* (其余 .book-card, .book-image 等样式不变) */
.book-card {
  margin-bottom: 20px;
}
.book-card-link {
  text-decoration: none;
  color: inherit;
}
.book-image {
  width: 100%;
  height: 250px;
  display: block;
}
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