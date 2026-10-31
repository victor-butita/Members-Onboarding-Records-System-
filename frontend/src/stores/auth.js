import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('mors_token') || null,
    user: JSON.parse(localStorage.getItem('mors_user') || 'null'),
    isLoading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    unit: (state) => state.user?.unit || '',
    role: (state) => state.user?.role || '',
    isSuperUser: (state) => state.user?.role === 'SUPER_USER' || state.user?.unit === 'SYSTEM_ADMIN',
    mustChangePassword: (state) => state.user?.must_change_password || false,
    canAccessUnit: (state) => (allowedUnits) => {
      if (!state.user) return false
      if (state.user.unit === 'SYSTEM_ADMIN') return true
      return allowedUnits.includes(state.user.unit)
    }
  },
  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', { username, password })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('mors_token', this.token)
        localStorage.setItem('mors_user', JSON.stringify(this.user))
        return response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Sign-in failed. Please check credentials.'
        throw err
      } finally {
        this.isLoading = false
      }
    },
    async changePassword(currentPassword, newPassword) {
      const response = await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      if (this.user) {
        this.user.must_change_password = false
        localStorage.setItem('mors_user', JSON.stringify(this.user))
      }
      return response.data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('mors_token')
      localStorage.removeItem('mors_user')
    }
  }
})
