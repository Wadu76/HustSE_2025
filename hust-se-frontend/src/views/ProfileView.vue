<template>
  <div class="profile-container">
    <h2>个人资料</h2>

    <div v-if="!userStore.user">
      <p>请先 <router-link to="/login">登录</router-link> 查看您的资料。</p>
    </div>

    <div v-else>
      <div class="form-group">
        <label>手机号 (只读):</label>
        <input type="text" :value="userStore.user.phone" disabled />
      </div>

      <div class="form-group">
        <label for="username">用户名:</label>
        <input id="username" v-model="editableUser.username" type="text" />
      </div>
      
      <div class="form-group">
        <label for="major">专业:</label>
        <input id="major" v-model="editableUser.major" type="text" />
      </div>

      <div class="form-group">
        <label for="grade">年级:</label>
        <input id="grade" v-model="editableUser.grade" type="text" />
      </div>

      <button @click="handleUpdateProfile">更新资料</button>
      <p v-if="message" class="message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore'; // 1. 导入用户 store

const userStore = useUserStore(); // 2. 获取 store 实例
const message = ref('');

//3. 【核心】创建一个新的 ref 来存储 *可编辑* 的用户信息
//    我们不希望 v-model 直接修改 Pinia store
const editableUser = ref({
  username: '',
  major: '',
  grade: ''
});

// 4. 页面加载时，用 Pinia store 中的数据填充这个可编辑的 ref
onMounted(() => {
  if (userStore.user) {
    editableUser.value.username = userStore.user.username;
    // (我们从 user.py 的 to_dict() 得知，userStore.user 中可能没有 major 和 grade)
    // (我们最好是从 GET /user/info 获取完整信息)
    
    // 【改进】为了获取最新的完整信息 (包括 major/grade)，我们调用 GET /user/info
    fetchFullUserInfo();
  }
});

// 4.1 【改进】从后端获取完整的、最新的用户信息
async function fetchFullUserInfo() {
    try {
        const response = await apiClient.get('/user/info'); //
        if (response.data.code === 200) {
            const fullUser = response.data.data;
            // 用后端返回的完整数据填充表单
            editableUser.value.username = fullUser.usernme; // 注意：user.py to_dict 中可能是 'usernme'
            editableUser.value.major = fullUser.major;
            editableUser.value.grade = fullUser.grade;
            
            // 同时更新 Pinia store，确保它是最新的
            // (LoginView 只存储了 id, username, phone)
            userStore.setUser(fullUser); 
        } else {
            message.value = '获取最新用户信息失败';
        }
    } catch (err) {
        message.value = '网络错误，无法获取用户信息';
    }
}


// 5. 定义更新资料的函数
async function handleUpdateProfile() {
  message.value = '更新中...';

  // 6. 准备要发送的数据 (只包含允许修改的字段)
  const dataToUpdate = {
    username: editableUser.value.username,
    major: editableUser.value.major,
    grade: editableUser.value.grade
  };

  try {
    // 7. 调用后端的 PUT /user/info 接口
    const response = await apiClient.put('/user/info', dataToUpdate);
    
    if (response.data.code === 200) {
      message.value = '用户信息更新成功！';
      
      // 8. 【重要】更新成功后，必须同步更新 Pinia store
      userStore.setUser(response.data.data);
      
    } else {
      // 显示后端返回的错误，例如 "用户名已存在"
      message.value = `更新失败: ${response.data.msg}`;
    }
  } catch (error) {
    console.error('更新资料失败:', error);
    if (error.response) {
      message.value = `更新失败: ${error.response.data.msg}`;
    } else {
      message.value = '更新失败，请检查网络。';
    }
  }
}
</script>

<style scoped>
/* 我们可以复用 RegisterView 的样式 */
.profile-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
}
.form-group input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
/* 禁用输入框的样式 */
.form-group input:disabled {
  background-color: #f0f0f0;
  color: #888;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.message {
  margin-top: 15px;
  color: green; /* 默认显示成功消息 */
}
/* 如果消息包含“失败”，则显示为红色 */
.message:containing("失败") {
    color: red;
}
</style>