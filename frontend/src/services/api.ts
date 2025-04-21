import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = localStorage.getItem('token');

    // 打印令牌信息，便于调试
    console.log('Token from localStorage:', token ? 'exists' : 'not found');

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Added Authorization header');
    }

    return config;
  },
  (error: AxiosError) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('Response success:', response.config.url);
    return response;
  },
  (error: AxiosError) => {
    console.error('Response error:', error.response?.status, error.config?.url);

    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      console.log('401 Unauthorized error detected');

      // 如果是登录请求，不清除令牌和重定向
      const isLoginRequest = error.config?.url?.includes('/login/');
      if (!isLoginRequest) {
        console.log('Not a login request, clearing tokens and redirecting');
        // Clear auth tokens from localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');

        // Redirect to login page
        window.location.href = '/login';
      } else {
        console.log('Login request failed with 401');
      }
    }

    return Promise.reject(error);
  }
);

export default api;
