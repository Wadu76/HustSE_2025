<template>
  <div class="create-book-container">
    <h2>发布一本新书</h2>
    
    <form @submit.prevent="handleCreateBook">
      
      <div class="form-group">
        <label for="title">书名:</label>
        <input id="title" v-model="title" type="text" required />
      </div>
      
      <div class="form-group">
        <label for="course_tag">课程标签:</label>
        <input id="course_tag" v-model="course_tag" type="text" required />
      </div>

      <div class="form-group">
        <label for="price">价格 (元):</label>
        <input id="price" v-model="price" type="number" step="0.1" required />
      </div>

      <div class="form-group">
        <label for="condition">新旧程度 (1-5):</label>
        <input id="condition" v-model="condition" type="number" min="1" max="5" required />
      </div>
      
      <div class="form-group">
        <label for="description">描述:</label>
        <textarea id="description" v-model="description"></textarea>
      </div>

      <div class="form-group">
        <label for="image">上传图片:</label>
        <input id="image" type="file" @change="onFileSelected" accept="image/*" />
      </div>
      
      <button type="submit">确认发布</button>
      
      <p v-if="message" class="message">{{ message }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '../api/api.js'; // 导入 axios 实例

// --- 绑定表单的响应式变量 ---
const title = ref('');
const course_tag = ref('');
const price = ref(0);
const condition = ref(3); // 默认值
const description = ref('');
const message = ref('');

// 2. 【核心】创建一个 ref 来存储用户选择的 *文件对象*
const selectedFile = ref(null);

// 3. 【核心】当用户选择文件时，@change 事件会调用这个函数
function onFileSelected(event) {
  // event.target.files 是一个文件列表
  // 我们只取第一个文件
  selectedFile.value = event.target.files[0];
}

// 4. 【核心】表单提交函数
async function handleCreateBook() {
  message.value = '发布中...';

  // 5. 检查是否登录 (稍后我们会用 Pinia 检查)
  // ...

  // 6. 检查是否选了文件 (我们暂时不强制要求上传图片)
  if (selectedFile.value) {
    console.log("即将上传的文件:", selectedFile.value);
  }

  // 7. 【关键】创建 FormData 对象
  //    因为我们发送的是 multipart/form-data, 而不是 JSON
  const formData = new FormData();
  
  // 8. 把所有文本数据 append 到 FormData 中
  //    (Key 必须和后端 request.form.get('key') 一致)
  formData.append('title', title.value);
  formData.append('course_tag', course_tag.value);
  formData.append('price', price.value);
  formData.append('condition', condition.value);
  formData.append('description', description.value);
  
  // 9. 如果有文件，把文件 append 进去
  //    (Key 'image' 必须和后端 request.files.get('image') 一致)
  if (selectedFile.value) {
    formData.append('image', selectedFile.value);
  }

  try {
    // 10. 发送请求
    const response = await apiClient.post('/book/create', formData, {
      // Axios 在发送 FormData 时会自动设置正确的 Content-Type (multipart/form-data)
      // 我们不需要额外配置 headers
    });
    
    message.value = '发布成功！';
    console.log('发布成功:', response.data.data);
    // 可以在这里清空表单，或者跳转到首页
    // ...

  } catch (error) {
    if (error.response) {
      if (error.response.status === 401) {
        message.value = '请先登录后再发布！';
      } else {
        message.value = `发布失败: ${error.response.data.msg}`;
      }
    } else {
      message.value = '发布失败，请检查网络。';
    }
    console.error('发布失败:', error);
  }
}
</script>

<style scoped>
.create-book-container {
  max-width: 500px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
.form-group input[type="file"] {
  width: 100%;
}
.message {
  margin-top: 15px;
  color: red;
}
</style>
