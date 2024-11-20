<template>
    <div class="game-detail">
      <h2>游戏详情</h2>
      
      <div v-if="loading">加载中...</div>
      
      <div v-else>
        <div v-if="error" class="error">{{ error }}</div>
        
        <div v-else>
          <div class="game-info">
            <p><strong>游戏ID：</strong> {{ game.game_id }}</p>
            <p><strong>开始时间：</strong> {{ formatDate(game.start_time) }}</p>
            <p><strong>结束时间：</strong> {{ game.end_time ? formatDate(game.end_time) : '进行中' }}</p>
            <p><strong>结果：</strong> {{ game.result ? game.result : '未知' }}</p>
          </div>
          
          <div class="moves">
            <h3>走棋记录</h3>
            <table>
              <thead>
                <tr>
                  <th>序号</th>
                  <th>玩家</th>
                  <th>走棋</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(move, index) in game.moves" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td>{{ move.player === 'white' ? '白方' : '黑方' }}</td>
                  <td>{{ move.move }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="final-position">
            <h3>最终棋盘状态</h3>
            <div id="board"></div>
            <p><strong>FEN：</strong> {{ game.fen_positions[game.fen_positions.length - 1] }}</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from './axios'; // 确保路径正确
  import Chessboard from 'chessboardjs-vue'; // 使用 chessboard.js
  import 'chessboardjs-vue/chessboard-1.0.0.css'; // 使用 chessboard.js 的 CSS
  
  export default {
    name: 'GameDetail',
    data() {
      return {
        game: null,
        loading: true,
        error: '',
        board: null,
      };
    },
    methods: {
      async fetchGameDetail() {
        const gameId = this.$route.params.game_id;
  
        if (!gameId) {
          this.error = '无效的游戏ID。';
          this.loading = false;
          return;
        }
  
        try {
          const response = await axios.get(`/game/${gameId}`);
          this.game = response.data.game;
  
          // 初始化棋盘，显示最终FEN位置
          const finalFEN = this.game.fen_positions[this.game.fen_positions.length - 1];
          this.initializeBoard(finalFEN);
        } catch (err) {
          console.error(err);
          this.error = err.response?.data?.message || '获取游戏详情时发生错误。';
        } finally {
          this.loading = false;
        }
      },
      initializeBoard(fen) {
        if (this.board) {
          this.board.destroy();
        }
  
        this.board = Chessboard('board', {
          position: fen,
          draggable: false,
          pieceTheme: 'https://cdnjs.cloudflare.com/ajax/libs/chessboard-js/1.0.0/img/chesspieces/wikipedia/{piece}.png',
        });
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
      this.fetchGameDetail();
    },
    beforeUnmount() {
      if (this.board) {
        this.board.destroy();
      }
    },
  };
  </script>
  
  <style scoped>
  .game-detail {
    padding: 20px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .game-info p {
    font-size: 16px;
    margin: 5px 0;
  }
  
  .moves {
    margin-top: 20px;
  }
  
  .moves table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .moves th, .moves td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
  }
  
  .moves th {
    background-color: #f2f2f2;
  }
  
  .final-position {
    margin-top: 20px;
    text-align: center;
  }
  
  #board {
    margin: 0 auto;
  }
  
  .error {
    color: red;
    text-align: center;
    margin-top: 20px;
  }
  </style>