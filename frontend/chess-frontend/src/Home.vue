<!-- Home.vue -->
<template>
    <div class="home">
      <h1>欢迎来到AI象棋游戏</h1>
      <div v-if="isAuthenticated">
        <p>您好，{{ username }}！</p>
        <button @click="startNewGame">开始新游戏</button>
        <button @click="viewGameHistory">查看游戏历史</button>
      </div>
      <div v-else>
        <p>请先登录或注册以开始游戏。</p>
        <router-link to="/login">
          <button>登录</button>
        </router-link>
        <router-link to="/register">
          <button>注册</button>
        </router-link>
      </div>
    </div>
  </template>
  
  <script>
  import axios from './axios'; // 确保路径正确
  
  export default {
    name: 'HomePage',
    data() {
      return {
        isAuthenticated: false,
        username: '',
      };
    },
    methods: {
      async checkAuthentication() {
        const token = localStorage.getItem('token');
        if (token) {
          try {
            // 可选：验证 token 的有效性，具体实现视后端而定
            // 例如，发送请求到后端验证 token
            const response = await axios.get('/verify_token');
            if (response.data.valid) {
              this.isAuthenticated = true;
              this.username = response.data.username;
            } else {
              this.isAuthenticated = false;
              this.username = '';
            }
          } catch (error) {
            console.error('Token 验证失败:', error);
            this.isAuthenticated = false;
            this.username = '';
          }
        } else {
          this.isAuthenticated = false;
          this.username = '';
        }
      },
      startNewGame() {
        this.$router.push('/ai-chess');
      },
      viewGameHistory() {
        this.$router.push('/game-history');
      },
    },
    mounted() {
      this.checkAuthentication();
    },
  };
  </script>
  
  <style scoped>
  .home {
    text-align: center;
    margin-top: 50px;
  }
  
  button {
    margin: 10px;
    padding: 10px 20px;
    font-size: 16px;
  }
  
  p {
    font-size: 18px;
  }
  </style>