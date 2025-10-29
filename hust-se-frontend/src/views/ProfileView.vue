<template>
  <div class="profile-container">
    <el-card header="个人资料">
      
      <div v-if="!userStore.user">
        <p>请先 <router-link to="/login">登录</router-link> 查看您的资料。</p>
      </div>

      <el-form 
        v-else 
        :model="editableUser" 
        label-width="80px"
        v-loading="loading"
      >
        
        <el-form-item label="手机号:">
          <el-input :value="userStore.user.phone" disabled />
        </el-form-item>

        <el-form-item label="用户名:">
          <el-input v-model="editableUser.username" />
        </el-form-item>
        
        <el-form-item label="专业:">
          <el-input v-model="editableUser.major" placeholder="请输入您的专业" />
        </el-form-item>

        <el-form-item label="年级:">
          <el-input v-model="editableUser.grade" placeholder="例如：大一" />
        </el-form-item>

        <el-form-item label="信用分:">
          <el-input v-if="userStore.user.credit" :value="userStore.user.credit" disabled />
          <el-input v-else value="加载中..." disabled />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleUpdateProfile" 
            :loading="updateLoading"
            style="width: 100%;"
          >
            更新资料
          </el-button>
        </el-form-item>

      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import apiClient from '../api/api.js';
import { useUserStore } from '../stores/userStore';
import { ElMessage } from 'element-plus'; // 导入 ElMessage

const userStore = useUserStore();
const loading = ref(true); // 页面加载
const updateLoading = ref(false); // 更新按钮加载

// 【修改】使用 reactive 更适合表单
const editableUser = reactive({
  username: '',
  major: '',
  grade: ''
});

onMounted(() => {
  if (userStore.user) {
    fetchFullUserInfo();
  } else {
    loading.value = false;
  }
});

async function fetchFullUserInfo() {
    loading.value = true;
    try {
        const response = await apiClient.get('/user/info');
        if (response.data.code === 200) {
            const fullUser = response.data.data;
            
            // 【注意】检查您的 user.py 中的拼写！
            // 如果您已将 user.py 改为 'username'
            editableUser.username = fullUser.username; 
            // 如果您还未修改 user.py，请使用 'usernme'
            // editableUser.username = fullUser.usernme; 
            
            editableUser.major = fullUser.major;
            editableUser.grade = fullUser.grade;
            
            // 同步更新 Pinia store
            userStore.setUser(fullUser); 
        } else {
            ElMessage.error('获取最新用户信息失败');
        }
    } catch (err) {
        ElMessage.error('网络错误，无法获取用户信息');
    } finally {
        loading.value = false;
    }
}

async function handleUpdateProfile() {
  updateLoading.value = true;

  // dataToUpdate 会自动包含来自 editableUser 的最新值
  try {
    const response = await apiClient.put('/user/info', editableUser);
    
    if (response.data.code === 200) {
      ElMessage.success('用户信息更新成功！');
      // 同步更新 Pinia store
      userStore.setUser(response.data.data);
    } else {
      ElMessage.error(`更新失败: ${response.data.msg}`);
    }
  } catch (error) {
    console.error('更新资料失败:', error);
    if (error.response) {
      ElMessage.error(`更新失败: ${error.response.data.msg}`);
    } else {
      ElMessage.error('更新失败，请检查网络。');
    }
  } finally {
    updateLoading.value = false;
  }
}
</script>

<style scoped>
/* 旧的样式 已不再需要 */
.profile-container {
  max-width: 500px; /* 稍微加宽 */
  margin: 50px auto;
}
</style>