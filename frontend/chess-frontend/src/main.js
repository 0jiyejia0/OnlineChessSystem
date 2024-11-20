// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from './axios';
import Chessboard from 'chessboardjs-vue'; // 导入 Chessboard 组件
import 'chessboardjs-vue/chessboard-1.0.0.css'; // 导入 Chessboard 的 CSS

const app = createApp(App);
app.config.globalProperties.$axios = axios; // 全局注册 axios
app.use(router);
app.component('ChessboardJs', Chessboard); // 全局注册 Chessboard
app.mount('#app');