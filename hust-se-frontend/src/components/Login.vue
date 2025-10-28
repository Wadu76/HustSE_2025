<template>
  <div class="login-container">
    <h2>校园二手书平台登录</h2>
    
    <div class="form-group">
      <label for="phone">手机号:</label>
      <input id="phone" v-model="phone" type="text" placeholder="请输入手机号" />
    </div>
    
    <div class="form-group">
      <label for="password">密码:</label>
      <input id="password" v-model="password" type="password" placeholder="请输入密码" />
    </div>
    
    <button @click="handleLogin">登录</button>
    
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
// 1. 导入我们配置好的 apiClient
import apiClient from '../api/api.js';

// 2. 创建 "响应式变量" 来绑定表单输入
const phone = ref('');     // 绑定手机号输入框
const password = ref('');  // 绑定密码输入框
const message = ref('');   // 用于显示后端返回的消息

// 3. 定义登录按钮点击时要执行的函数
async function handleLogin() {
  // 检查输入是否为空
  if (!phone.value || !password.value) {
    message.value = '手机号和密码不能为空';
    return;
  }
  
  message.value = '登录中...'; // 提示用户
  
  try {
    // 4. 使用 apiClient 调用后端 /user/login 接口
    const response = await apiClient.post('/user/login', {
      phone: phone.value,
      password: password.value
    });
    
    // 5. 处理成功响应
    // response.data 对应我们后端 jsonify 返回的整个字典
    message.value = response.data.msg; // "登录成功"
    
    // 打印后端返回的用户信息到控制台
    console.log('登录成功，用户信息:', response.data.data.user);
    
    // 【重要】登录成功后，浏览器会自动保存 Session Cookie
    // 我们不需要做任何操作！
    
  } catch (error) {
    // 6. 处理失败响应
    if (error.response) {
      // 如果是后端返回的错误 (例如 "手机号或密码错误")
      message.value = error.response.data.msg;
    } else {
      // 如果是网络错误或CORS错误
      message.value = '登录失败，请检查网络或联系管理员';
    }
    console.error(error);
  }
}
</script>

<style scoped>
.login-container {
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
  box-sizing: border-box; /* 确保 padding 不会撑大宽度 */
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
  color: red;
}
</style>