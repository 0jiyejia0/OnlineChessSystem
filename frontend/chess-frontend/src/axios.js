// src/axios.js
import axios from 'axios';
import router from './router'; // 确保路径正确

const instance = axios.create({
  baseURL: 'http://localhost:5000', // 后端 API 的基础 URL，确保端口和路径正确
});

// 添加请求拦截器，附加 JWT 令牌
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器，处理全局错误，如401未授权
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token无效或过期，重定向到登录页
      localStorage.removeItem('token');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default instance;