import axios from 'axios';

// Базовый URL берем из переменных окружения Vite (или ставим локальный по умолчанию)
const API_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор: перед каждым запросом достаем токен из localStorage
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Интерцептор: если бэкенд вернул 401 (токен протух), разлогиниваем юзера
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Опционально: принудительный редирект на /login
      window.location.href = '/login'; 
    }
    return Promise.reject(error);
  }
);