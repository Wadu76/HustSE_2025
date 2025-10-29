<template>
  <div id="layout">
    <nav>
      <router-link to="/">首页</router-link> | 
      <router-link to="/login">登录</router-link> |
      <router-link to="/register">注册</router-link> |
      <router-link to="/create-book">发布书籍</router-link> |
      <router-link to="/orders">我的订单</router-link> |

      <router-link to="/profile">个人资料</router-link>
      </nav>
    
    <main>
      <router-view />
    </main>
    
  </div>
</template>

<script setup>
</script>

<style>
/* 全局样式  */
nav {
  padding: 20px;
  text-align: center;
  background-color: #f4f4f4;
}
main {
  padding: 20px;
}
</style>