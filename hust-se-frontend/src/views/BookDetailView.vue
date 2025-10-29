<template>
  <div class="detail-container">
    <div v-if="loading" v-loading.fullscreen.lock="loading"></div>
    <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />

    <el-row v-if="book" :gutter="30">
      
      <el-col :span="10">
        <el-image :src="getImageUrl(book.images)" class="book-image" fit="cover">
          <template #placeholder>
            <div class="image-placeholder">加载中...</div>
          </template>
          <template #error>
            <div class="image-placeholder">无图片</div>
          </template>
        </el-image>
      </el-col>

      <el-col :span="14">
        <h1>{{ book.title }}</h1>
        <p class="description">{{ book.description || '暂无描述' }}</p>

        <el-descriptions :column="2" border class="book-info">
          
          <el-descriptions-item label="价格">
            <span class="price">¥ {{ book.price }}</span>
          </el-descriptions-item>

          <el-descriptions-item label="作者">
            {{ book.author || '未知' }}
          </el-descriptions-item>

          <el-descriptions-item label="新旧程度">
            <el-tag size="small">{{ book.condition }}</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="课程标签">
            <el-tag size="small">{{ book.course_tag }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="卖家">
            {{ book.seller_name }}
          </el-descriptions-item>
          <el-descriptions-item label="卖家信用">
            <el-tag :type="getCreditTagType(book.seller_credit)" effect="dark">
              {{ book.seller_credit }}
            </el-tag>
          </el-descriptions-item>
          </el-descriptions>
        
        <el-button 
          type="primary"
          size="large"
          @click="handleBuyNow" 
          :disabled="book.status !== 1"
          class="buy-button"
        >
          <el-icon><ShoppingIcon /></el-icon>
          {{ book.status === 1 ? '立即购买' : '已售出' }}
        </el-button>
        
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/userStore';
import apiClient from '../api/api.js';
// 【UI 升级】导入 ElMessage 和 ElMessageBox
import { ElMessage, ElMessageBox } from 'element-plus'; 
// 【UI 升级】导入图标
import { ShoppingCartFull as ShoppingIcon } from '@element-plus/icons-vue';

const BACKEND_URL = apiClient.defaults.baseURL;

const book = ref(null);
const loading = ref(true); // 默认设为 true
const error = ref(null);
const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// (fetchBookDetail 函数不变)
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

// (getImageUrl 函数不变)
function getImageUrl(imagePath) {
  if (!imagePath) return '';
  return `${BACKEND_URL}${imagePath}`;
}

onMounted(() => {
  fetchBookDetail();
});

// 【UI 升级】handleBuyNow 函数修改为使用 Element Plus
const handleBuyNow = async () => {
  if (!userStore.user) {
    ElMessage.warning('请先登录后再购买！');
    router.push('/login');
    return;
  }

  if (userStore.user.id === book.value.seller_id) {
    ElMessage.error('不能购买自己发布的书籍！');
    return;
  }
  
  // 【UI 升级】使用 ElMessageBox 确认
  try {
    await ElMessageBox.confirm(
      `您确定要以 ¥${book.value.price} 的价格购买《${book.value.title}》吗？`,
      '订单确认',
      {
        confirmButtonText: '确定购买',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
  } catch (cancel) {
    // 用户点击了“取消”
    ElMessage.info('订单已取消');
    return;
  }

  // (调用 API 部分不变)
  try {
    const response = await apiClient.post('/order/create', {
      book_id: book.value.id
    });

    if (response.data.code === 200) {
      ElMessage.success('订单创建成功！'); // UI 升级
      book.value.status = 0; 
    } else {
      ElMessage.error(`购买失败: ${response.data.msg}`); // UI 升级
    }
  } catch (error) {
    console.error('创建订单失败:', error);
    if (error.response && error.response.data.msg) {
        ElMessage.error(`创建订单时出错: ${error.response.data.msg}`);
    } else {
        ElMessage.error('创建订单时发生网络错误');
    }
  }
};

// --- 【新增功能】辅助函数：根据信用分返回标签类型 ---
function getCreditTagType(credit) {
  if (credit >= 100) return 'success'; // 优秀
  if (credit >= 80) return 'warning'; // 良好
  if (credit < 80) return 'danger';  // 较差
  return 'info'; // 默认
}
</script>

<style scoped>
/* 【UI 升级】使用新的样式
  (这对应您上次上传的 style 文件)
*/
.detail-container {
  max-width: 1000px;
  margin: 0 auto;
}
.book-image {
  width: 100%;
  height: 450px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 450px;
  background-color: #f5f7fa;
  color: #c0c4cc;
}
h1 {
  font-size: 2em;
  margin-top: 0;
}
.description {
  font-size: 1em;
  color: #606266;
  margin-bottom: 20px;
}
.book-info {
  margin-bottom: 20px;
}
/* el-descriptions-item 里的价格 */
.price {
  font-size: 1.5em;
  color: #e44d26;
  font-weight: bold;
}
.buy-button {
  width: 100%;
  margin-top: 20px;
}
/* el-button 里的图标 */
.el-icon {
  margin-right: 8px;
}
</style>