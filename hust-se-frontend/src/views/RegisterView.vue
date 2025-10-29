<template>
  <div class="register-container">
    <h2>注册新用户</h2>
    
    <div class="form-group">
      <label for="phone">手机号:</label>
      <input id="phone" v-model="phone" type="text" placeholder="请输入手机号" />
    </div>
    
    <div class="form-group">
      <label for="username">用户名:</label>
      <input id="username" v-model="username" type="text" placeholder="请输入用户名" />
    </div>

    <div class="form-group">
      <label for="password">密码:</label>
      <input id="password" v-model="password" type="password" placeholder="请输入密码" />
    </div>
    
    <button @click="handleRegister">注册</button>
    
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/api.js';

const phone = ref('');
const username = ref('');
const password = ref('');
const message = ref('');

const router = useRouter();

async function handleRegister() {
  // 1. 前端基本校验
  if (!phone.value || !password.value || !username.value) {
    message.value = '手机号、用户名和密码均不能为空';
    return;
  }
  message.value = '注册中...'; 
  
  try {
    // 2. 调用后端 /user/register 接口
    const response = await apiClient.post('/user/register', {
      phone: phone.value,
      username: username.value,
      password: password.value
    });
    
    // 3. 处理成功响应
    message.value = `${response.data.msg}！即将跳转到登录页面...`; // "注册成功"
    
    // 4. 注册成功后，自动跳转到登录页
    setTimeout(() => {
      router.push('/login'); // 跳转到登录
    }, 1500); // 延迟 1.5 秒，让用户看到成功提示
    
  } catch (error) {
    // 5. 处理错误响应
    if (error.response) {
      // 显示后端返回的错误，例如 "手机号已被注册"
      message.value = error.response.data.msg;
    } else {
      message.value = '注册失败，请检查网络或联系管理员';
    }
    console.error('注册时发生错误:', error); 
  }
}
</script>

<style scoped>
/* 我们可以复用 LoginView 的样式 */
.register-container {
  max-width: 300px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  text-align: center;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
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
  /* 根据消息类型改变颜色会更好，但暂时先用红色 */
  color: red; 
}
/* 如果注册成功，消息显示为绿色 */
.message:not(error) {
    color: green;
}
</style>