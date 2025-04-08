import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance
const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('token');

    // If token exists, add to headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    // Handle request error
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    // Handle successful responses
    return response.data;
  },
  (error) => {
    // Handle response error
    const message = error.response?.data?.detail || 'An error occurred';
    
    // Don't show toast for authentication errors
    if (error.response?.status !== 401) {
      toast.error(message);
    }

    // Handle token expiration
    if (error.response?.status === 401) {
      // Clear auth storage
      localStorage.removeItem('token');
      
      // Redirect to login if not already there
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default instance; 