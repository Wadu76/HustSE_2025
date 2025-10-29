<template>
  <el-card class="login-card" header="校园二手书平台登录">
    
    <el-form :model="loginForm" label-width="80px">
      
      <el-form-item label="手机号:">
        <el-input v-model="loginForm.phone" placeholder="请输入手机号" />
      </el-form-item>
      
      <el-form-item label="密码:">
        <el-input 
          v-model="loginForm.password" 
          type="password" 
          placeholder="请输入密码" 
          show-password 
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleLogin" 
          :loading="loading"
          style="width: 100%;"
        >
          登录
        </el-button>
      </el-form-item>
      
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore.js'; 
// 【新增】导入 ElMessage 用于消息提示
import { ElMessage } from 'element-plus'; 

// 1. 【修改】使用 reactive 定义表单数据
const loginForm = reactive({
  phone: '',
  password: ''
});
const loading = ref(false); // 控制登录按钮的加载状态

const userStore = useUserStore(); 
const router = useRouter(); 

async function handleLogin() {
  // 2. 校验表单
  if (!loginForm.phone || !loginForm.password) {
    ElMessage.error('手机号和密码不能为空'); // 【修改】使用 ElMessage 提示
    return;
  }
  loading.value = true; // 开始登录，按钮显示加载
  
  try {
    // 3. 发送请求 (数据来自 loginForm)
    const response = await apiClient.post('/user/login', {
      phone: loginForm.phone,
      password: loginForm.password
    });
    
    ElMessage.success('登录成功！'); // 【修改】使用 ElMessage 提示
    
    // 存入 Pinia 仓库
    userStore.setUser(response.data.data.user);
    
    // 4. 登录成功后，自动跳转到首页
    setTimeout(() => {
      router.push('/');
    }, 500); 
    
  } catch (error) {
    // 5. 【修改】使用 ElMessage 显示后端错误
    if (error.response) {
      ElMessage.error(error.response.data.msg);
    } else {
      ElMessage.error('登录失败，请检查网络');
    }
    console.error('登录时发生错误:', error); 
  } finally {
    loading.value = false; // 无论成功失败，结束加载
  }
}
</script>

<style scoped>
/* 旧的样式 已不再需要
  我们只需要设置卡片的宽度和居中
*/
.login-card {
  max-width: 450px;
  margin: 50px auto; /* 居中 */
}
</style>