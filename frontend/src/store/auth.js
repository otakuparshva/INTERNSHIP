import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from '../api/axios';
import { jwtDecode } from 'jwt-decode';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post('/auth/login', { email, password });
          const { user, token } = response.data;
          set({ user, token, isAuthenticated: true, isLoading: false });
          return true;
        } catch (error) {
          set({ error: error.response?.data?.message || 'Login failed', isLoading: false });
          return false;
        }
      },

      // Register
      register: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.post('/auth/register', userData);
          const { user, token } = response.data;
          set({ user, token, isAuthenticated: true, isLoading: false });
          return true;
        } catch (error) {
          set({ error: error.response?.data?.message || 'Registration failed', isLoading: false });
          return false;
        }
      },

      // Logout
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false, error: null });
      },

      // Check if token is expired
      checkAuth: () => {
        const { token } = get();
        if (!token) return false;

        try {
          const decoded = jwtDecode(token);
          const currentTime = Date.now() / 1000;

          if (decoded.exp < currentTime) {
            get().logout();
            return false;
          }

          // Set token in axios headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },

      // Update user profile
      updateProfile: async (userData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await axios.put('/api/auth/profile', userData);
          set({
            user: { ...get().user, ...response.data },
            isLoading: false,
          });
          return true;
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Profile update failed',
            isLoading: false,
          });
          return false;
        }
      },

      // Reset password
      resetPassword: async (email) => {
        set({ isLoading: true, error: null });
        try {
          await axios.post('/api/auth/reset-password', { email });
          set({ isLoading: false });
          return true;
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Password reset failed',
            isLoading: false,
          });
          return false;
        }
      },

      // Update password
      updatePassword: async (currentPassword, newPassword) => {
        set({ isLoading: true, error: null });
        try {
          await axios.put('/api/auth/update-password', {
            current_password: currentPassword,
            new_password: newPassword,
          });
          set({ isLoading: false });
          return true;
        } catch (error) {
          set({
            error: error.response?.data?.detail || 'Password update failed',
            isLoading: false,
          });
          return false;
        }
      },

      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export default useAuthStore; 