<template>
  <el-card class="register-card" header="注册新用户">
    
    <el-form 
      :model="registerForm" 
      :rules="rules"
      ref="registerFormRef"
      label-width="80px"
    >
      
      <el-form-item label="手机号:" prop="phone">
        <el-input v-model="registerForm.phone" placeholder="请输入手机号" />
      </el-form-item>
      
      <el-form-item label="用户名:" prop="username">
        <el-input v-model="registerForm.username" placeholder="请输入用户名" />
      </el-form-item>
      
      <el-form-item label="密码:" prop="password">
        <el-input 
          v-model="registerForm.password" 
          type="password" 
          placeholder="请输入密码" 
          show-password 
        />
      </el-form-item>
      
      <el-form-item label="确认密码:" prop="confirmPassword">
        <el-input 
          v-model="registerForm.confirmPassword" 
          type="password" 
          placeholder="请再次输入密码"
          show-password 
        />
      </el-form-item>

      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleRegister" 
          :loading="loading"
          style="width: 100%;"
        >
          立即注册
        </el-button>
      </el-form-item>

      <el-form-item>
        <el-button text @click="router.push('/login')" style="width: 100%;">
          已有账户？去登录
        </el-button>
      </el-form-item>
      
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../api/api.js';
import { ElMessage } from 'element-plus'; // 导入消息提示

const router = useRouter();
const loading = ref(false);
const registerFormRef = ref(); // 表单的引用

// 1. 【修改】使用 reactive 定义表单数据
const registerForm = reactive({
  phone: '',
  username: '',
  password: '',
  confirmPassword: ''
});

// 2. 【新增】表单验证规则
const validatePassConfirm = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.password) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const rules = reactive({
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validatePassConfirm, trigger: 'blur' }]
});


// 3. 【修改】注册函数
async function handleRegister() {
  if (!registerFormRef.value) return; // 检查表单引用是否存在

  // 3.1 【新增】表单验证
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请检查表单输入项');
      return;
    }

    // 3.2 验证通过，执行注册
    loading.value = true;
    try {
      // 调用后端 /user/register 接口
      const response = await apiClient.post('/user/register', {
        phone: registerForm.phone,
        username: registerForm.username,
        password: registerForm.password
        // 后端不需要 confirmPassword
      });
      
      ElMessage.success('注册成功！即将跳转到登录页面...');
      
      // 注册成功后，自动跳转到登录页
      setTimeout(() => {
        router.push('/login');
      }, 1500); 
      
    } catch (error) {
      if (error.response) {
        // 显示后端返回的错误，例如 "手机号已被注册"
        ElMessage.error(error.response.data.msg);
      } else {
        ElMessage.error('注册失败，请检查网络');
      }
    } finally {
      loading.value = false;
    }
  });
}
</script>

<style scoped>
/* 旧的样式已不再需要，风格与登录页保持一致 */
.register-card {
  max-width: 450px;
  margin: 50px auto;
}
</style>