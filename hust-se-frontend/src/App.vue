<template>
  <Login />
</template>

<script setup>
// 1. 从我们刚创建的文件中，导入 Login 组件
import Login from './components/Login.vue';

// 2. (App.vue 会自动注册这个组件，我们什么都不用做)
</script>

<style>
/* 我们可以保留或删除默认样式，先保留基础样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>