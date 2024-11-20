<template>
  <div>
    <h2>登录</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="用户名" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <button type="submit">登录</button>
    </form>
    <div v-if="message">{{ message }}</div>
  </div>
</template>

<script>
import axios from './axios'; 

export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      message: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:5000/login', {
          username: this.username,
          password: this.password
        });
        // 存储 token
        localStorage.setItem('token', response.data.token);
        this.message = '登录成功';
        this.$router.push('/'); // 登录成功后跳转到首页
      } catch (error) {
        this.message = error.response.data.message;
      }
    }
  }
};
</script>