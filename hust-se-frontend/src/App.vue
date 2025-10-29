<template>
  <el-container class="app-container">
    
    <el-header class="app-header">
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        :router="true"
        class="app-menu"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/create-book">发布书籍</el-menu-item>
        <el-menu-item index="/orders">我的订单</el-menu-item>
        <el-menu-item index="/profile">个人资料</el-menu-item>
        
        <div class="spacer"></div> 

        <template v-if="!userStore.user">
          <el-menu-item index="/login">登录</el-menu-item>
          <el-menu-item index="/register">注册</el-menu-item>
        </template>
        <template v-else>
          <el-sub-menu index="/profile-menu">
            <template #title>你好, {{ userStore.user.username }}</template>
            <el-menu-item index="/profile">个人资料</el-menu-item>
            <el-menu-item @click="handleLogout">退出登录</el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-header>
    
    <el-main class="app-main">
      <div class="main-content-wrapper">
        <router-view />
      </div>
    </el-main>
    
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from './stores/userStore'; // 导入 Pinia store
import { ElMessage, ElMessageBox } from 'element-plus';

// 1. 获取 store, route 和 router 实例
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

// 2. 计算当前激活的路由路径 (不变)
const activeIndex = computed(() => route.path);

// 3. 【新增】退出登录函数
const handleLogout = () => {
  ElMessageBox.confirm('您确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
  .then(() => {
    // 1. 清空 Pinia 中的用户信息
    userStore.clearUser();
    
    // 2. 提示用户
    ElMessage.success('退出成功！');
    
    // 3. 跳转到登录页 (或者首页)
    router.push('/login');
    
    // 4. (重要) 通知后端清除 Session (如果需要的话)
    //    由于我们是基于 Session 的，前端清除了 Pinia 状态，
    //    但后端的 Session 还在。最稳妥的方式是也调用一个后端的 /logout 接口。
    //    但目前我们没有这个接口，所以先只做前端清除。
  })
  .catch(() => {
    // 用户点击了“取消”
    ElMessage.info('已取消退出');
  });
};
</script>

<style>
/* 确保您的全局样式 (style.css 或这里的 <style>) 
  没有覆盖 Element Plus 的样式
*/
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
}

#app {
  text-align: left;
  padding: 0;
  max-width: none;
}

/* 布局样式 */
.app-container {
  min-height: 100vh;
}

.app-header {
  padding: 0;
  border-bottom: 1px solid #e6e6e6;
  /* 【新增】修复 el-menu 默认高度不撑满 header 的问题 
    (如果您的菜单看起来太矮)
  */
  height: 60px; /* Element Plus 菜单的默认高度 */
}

.app-menu {
  display: flex;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  border-bottom: none !important; /* 移除 el-menu 自己的底边框 */
}

.spacer {
  flex-grow: 1; /* 占据所有剩余空间 */
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
}

.main-content-wrapper {
  max-width: 1280px;
  margin: 0 auto;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
</style>