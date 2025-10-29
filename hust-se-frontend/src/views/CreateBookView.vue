<template>
  <div class="create-book-container">
    <el-card header="发布一本新书">
      
      <el_alert v-if="!userStore.user" type="warning" show-icon :closable="false">
        请先 <router-link to="/login">登录</router-link> 再发布书籍。
      </el_alert>

      <el-form 
        v-else
        :model="bookForm" 
        label-width="100px"
        v-loading="loading"
      >
        
        <el-form-item label="书名:" required>
          <el-input v-model="bookForm.title" placeholder="请输入书名" />
        </el-form-item>

        <el-form-item label="作者:">
          <el-input v-model="bookForm.author" placeholder="请输入作者" />
        </el-form-item>
        <el-form-item label="课程标签:" required>
          <el-input v-model="bookForm.course_tag" placeholder="例如：软件工程" />
        </el-form-item>

        <el-form-item label="价格 (元):" required>
          <el-input-number v-model="bookForm.price" :precision="2" :step="1" :min="0" />
        </el-form-item>
        
        <el-form-item label="新旧程度:" required>
          <el-rate v-model="bookForm.condition" :max="5" />
          <span style="margin-left: 10px;">({{ bookForm.condition }} 成新)</span>
        </el-form-item>

        <el-form-item label="描述:">
          <el-input v-model="bookForm.description" type="textarea" :rows="3" />
        </el-form-item>

        <el-form-item label="上传图片:">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            @change="handleFileChange"
            accept="image/*"
          >
            <template #trigger>
              <el-button type="primary">选择图片</el-button>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleCreateBook">
            确认发布
          </el-button>
        </el-form-item>
        
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);

// 【修改】使用 reactive 定义表单
const bookForm = reactive({
  title: '',
  author: '', // 【新增】
  course_tag: '',
  price: 0.0,
  condition: 3, // 默认 3 星
  description: '',
});

// 存储文件对象
const selectedFile = ref(null);
const uploadRef = ref(); // 用于 el-upload

// 文件变化时
function handleFileChange(file) {
  selectedFile.value = file.raw; // Element Plus 把文件放在 file.raw
}

// 【修改】提交表单
async function handleCreateBook() {
  if (!bookForm.title || !bookForm.course_tag || !bookForm.price) {
    ElMessage.error('书名、课程标签和价格是必填项');
    return;
  }

  loading.value = true;
  
  // 1. 创建 FormData
  const formData = new FormData();
  
  // 2. 添加表单数据
  formData.append('title', bookForm.title);
  formData.append('author', bookForm.author); // 【新增】
  formData.append('course_tag', bookForm.course_tag);
  formData.append('price', bookForm.price);
  formData.append('condition', bookForm.condition);
  formData.append('description', bookForm.description);
  
  // 3. 添加文件
  if (selectedFile.value) {
    formData.append('image', selectedFile.value);
  }

  try {
    // 4. 调用后端 API
    const response = await apiClient.post('/book/create', formData);
    
    if (response.data.code === 200) {
      ElMessage.success('书籍发布成功！');
      // 跳转到新书的详情页
      router.push(`/book/${response.data.data.id}`);
    } else {
      ElMessage.error(`发布失败: ${response.data.msg}`);
    }
  } catch (error) {
    if (error.response && error.response.status === 401) {
      ElMessage.error('请先登录后再发布！');
    } else {
      ElMessage.error('发布失败，请检查网络。');
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.create-book-container {
  max-width: 600px;
  margin: 20px auto;
}
</style>