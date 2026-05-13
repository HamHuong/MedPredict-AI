import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for auth errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect on /auth/me (expected 401 when not logged in)
    const url = error.config?.url || '';
    if (error.response?.status === 401 && !url.includes('/auth/me')) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default client;
