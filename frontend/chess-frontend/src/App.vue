<!-- App.vue -->
<template>
  <div id="app">
    <nav>
      <router-link to="/">主页</router-link>
      <router-link to="/register">注册</router-link>
      <router-link to="/login">登录</router-link>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>