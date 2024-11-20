<template>
  <div>
    <h2>AI 棋局</h2>
    <div id="board" style="width: 400px"></div>
    <div v-if="message">{{ message }}</div>  <!-- 显示提示消息 -->
  </div>
</template>

<script>
import axios from './axios';
import { Chess } from 'chess.js';
import Chessboard from 'chessboardjs-vue'; // 假设您使用 chessboardjs

export default {
  name: 'AiChess',
  data() {
    return {
      gameId: null,
      fen: '',
      loading: false,
      error: '',
      message: '',
      board: null,
    };
  },
  methods: {
    async startGame() {
      this.loading = true;
      this.error = '';
      this.message = '';
      try {
        // 调用后端 API 创建新游戏
        const response = await axios.post(
          '/start_game',
          {},
          {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          }
        );
        console.log('开始游戏的响应:', response.data);

        // 检查响应数据
        if (!response.data || !response.data.fen || !response.data.game_id) {
          throw new Error('游戏状态未返回');
        }

        // 设置游戏ID和FEN
        this.gameId = response.data.game_id;
        this.fen = response.data.fen;

        // 初始化或恢复棋盘位置
        this.restorePosition(this.fen);
        this.game = new Chess();
        this.board = Chessboard('board', {
          draggable: true,
          position: 'start',
          onDrop: this.onDrop,
        });
      } catch (err) {
        console.error('启动游戏时发生错误:', err);
        this.error = err.response?.data?.message || err.message || '发生错误，请重试！';
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
        pieceTheme: 'https://cdnjs.cloudflare.com/ajax/libs/chessboard.js/1.0.0/img/chesspieces/wikipedia/{piece}.png',
      });
    },

    async onDrop(source, target) {
      let move = null;
      const currentFen = this.game.fen();

      try {
        move = this.game.move({
          from: source,
          to: target,
          promotion: 'q',
        });
      } catch (error) {
        console.error(error);
        this.message = '发生错误，请重试！';
        return this.restorePosition(currentFen);
      }

      if (move === null) {
        this.message = '非法走子，请重新选择！';
        return this.restorePosition(currentFen);
      }

      const userMove = source + target;

      try {
        const response = await axios.post('http://localhost:5000/make_move', {
          game_id: this.gameId,
          user_move: userMove,
        });

        if (response.data.fen) {
          this.game.load(response.data.fen);
          this.board.position(response.data.fen);
          this.message = '';
        }

        if (response.data.ai_move) {
          this.message = 'AI 已走棋：' + response.data.ai_move;
        }

        if (response.data.message) {
          this.message = response.data.message;
        }
      } catch (error) {
        console.error(error);
        this.message = error.response?.data?.message || 'Error making move';
        this.restorePosition(currentFen);
      }
    },

    async makeMove(userMove) {
      try {
        const response = await axios.post('/make_move', {
          game_id: this.gameId,
          user_move: userMove
        });

        if (response.data.fen) {
          this.game.load(response.data.fen);
          this.board.position(response.data.fen);
          this.message = '';
        }

        if (response.data.ai_move) {
          // Apply AI move to the game
          const aiMove = this.game.move(response.data.ai_move);
          if (aiMove) {
            this.board.position(this.game.fen());
            this.message = 'AI 已走棋：' + response.data.ai_move;
          }
        }

        if (response.data.message) {
          this.message = response.data.message;
        }
      } catch (error) {
        console.error(error);
        this.message = 'Error making move';
      }
    },

    restorePosition(fen) {
      if (this.board) {
        this.board.position(fen);
      } else {
        // 初始化棋盘
        this.board = Chessboard('board', {
          draggable: true,
          position: fen,
          // 其他棋盘配置
        });
      }
    },
  },
  mounted() {
    this.startGame();
  }
};
</script>

<style scoped>
@import 'chessboardjs-vue/chessboard-1.0.0.css';
#board {
  width: 400px;
  margin-bottom: 10px;
}
div {
  color: red;
  font-weight: bold;
}
.error {
  color: red;
  font-weight: bold;
}

.message {
  color: green;
  font-weight: bold;
}

.loading {
  color: blue;
  font-style: italic;
}

#board {
  width: 400px;
  margin-bottom: 10px;
}
</style>