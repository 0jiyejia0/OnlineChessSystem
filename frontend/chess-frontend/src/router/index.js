// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../Home.vue';
import UserRegister from '../Register.vue';
import UserLogin from '../Login.vue';
import AiChess from '../AiChess.vue';
import GameHistory from '../GameHistory.vue';
import GameDetail from '../GameDetail.vue';

const routes = [
  { path: '/', component: Home, meta: { requiresAuth: true } },
  { path: '/register', component: UserRegister },
  { path: '/login', component: UserLogin },
  { path: '/ai-chess', component: AiChess, meta: { requiresAuth: true } },
  { path: '/game-history', component: GameHistory, meta: { requiresAuth: true } },
  { path: '/game/:game_id', component: GameDetail, meta: { requiresAuth: true } },
  // 其他路由
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 导航守卫
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const token = localStorage.getItem('token');

  if (requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;