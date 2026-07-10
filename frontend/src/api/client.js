import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor – attach JWT token if present
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor – handle auth errors globally
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (error.response?.status === 429 || error.response?.status === 502 || error.response?.status === 503) {
      // Dispatch global event for network/quota errors
      const event = new CustomEvent('network-quota-error', { 
        detail: error.response?.data?.detail 
      });
      window.dispatchEvent(event);
      // We still reject the promise so the caller can stop loading state, but we can suppress generic toasts if we want
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

export default client;
