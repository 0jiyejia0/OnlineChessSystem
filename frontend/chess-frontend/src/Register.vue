<template>
    <div>
      <h2>注册</h2>
      <form @submit.prevent="register">
        <input v-model="username" placeholder="用户名" required />
        <input v-model="password" type="password" placeholder="密码" required />
        <button type="submit">注册</button>
      </form>
      <div v-if="message">{{ message }}</div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'UserRegister',
    data() {
      return {
        username: '',
        password: '',
        message: ''
      };
    },
    methods: {
      async register() {
        try {
          const response = await axios.post('http://localhost:5000/register', {
            username: this.username,
            password: this.password
          });
          this.message = response.data.message;
          this.$router.push('/login'); // 注册成功后跳转到登录页面
        } catch (error) {
          this.message = error.response.data.message;
        }
      }
    }
  };
  </script>
  