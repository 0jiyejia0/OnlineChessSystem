<template>
    <div class="game-history">
      <h2>游戏历史</h2>
      <div v-if="loading">加载中...</div>
      <div v-else>
        <div v-if="games.length === 0">您还没有任何游戏记录。</div>
        <table v-else>
          <thead>
            <tr>
              <th>游戏ID</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>结果</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in games" :key="game.game_id">
              <td>{{ game.game_id }}</td>
              <td>{{ formatDate(game.start_time) }}</td>
              <td>{{ game.end_time ? formatDate(game.end_time) : '进行中' }}</td>
              <td>{{ game.result ? game.result : '未知' }}</td>
              <td>
                <router-link :to="`/game/${game.game_id}`">
                  <button>查看详情</button>
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </template>
  
  <script>
  import axios from './axios'; // 确保路径正确
  
  export default {
    name: 'GameHistory',
    data() {
      return {
        games: [],
        loading: true,
        error: '',
      };
    },
    methods: {
      async fetchGameHistory() {
        try {
          // 从 localStorage 获取 token
          const token = localStorage.getItem('token');
          if (!token) {
            this.error = '未检测到登录状态，请先登录。';
            this.loading = false;
            return;
          }
  
          // 调用 verify_token 获取 username（可选）
          await axios.get('/verify_token');
  
          // 获取游戏历史
          const response = await axios.get('/game_history');
          this.games = response.data.games;
        } catch (err) {
          console.error(err);
          this.error = err.response?.data?.message || '获取游戏历史时发生错误。';
        } finally {
          this.loading = false;
        }
      },
      formatDate(dateString) {
        const options = {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        };
        return new Date(dateString).toLocaleDateString(undefined, options);
      },
    },
    mounted() {
      this.fetchGameHistory();
    },
  };
  </script>
  
  <style scoped>
  .game-history {
    padding: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  
  thead {
    background-color: #f2f2f2;
  }
  
  th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: center;
  }
  
  th {
    background-color: #4CAF50;
    color: white;
  }
  
  button {
    padding: 6px 12px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #45a049;
  }
  
  .error {
    color: red;
    text-align: center;
    margin-top: 20px;
  }
  </style>