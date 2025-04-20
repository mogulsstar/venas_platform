import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { store } from '../store';
import { logout } from '../features/auth/authSlice';

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const state = store.getState();
    const token = state.auth.token;
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Dispatch logout action to clear auth state
      store.dispatch(logout());
    }
    
    return Promise.reject(error);
  }
);

export default api;
