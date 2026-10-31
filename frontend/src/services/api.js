import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add Bearer token interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mors_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercept 401 unauth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('mors_token')
      localStorage.removeItem('mors_user')
      if (window.location.pathname.startsWith('/dashboard') || 
          window.location.pathname.startsWith('/desk') ||
          window.location.pathname.startsWith('/clearance') ||
          window.location.pathname.startsWith('/gazette') ||
          window.location.pathname.startsWith('/reports') ||
          window.location.pathname.startsWith('/admin')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
