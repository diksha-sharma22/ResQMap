import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const authStorage = localStorage.getItem('auth-storage')
  if (authStorage) {
    const { state } = JSON.parse(authStorage)
    if (state.token) {
      config.headers.Authorization = `Bearer ${state.token}`
    }
  }
  return config
})

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: any) => api.post('/api/auth/register', data),
  getMe: () => api.get('/api/auth/me'),
}

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
  getRecentAlerts: (limit = 5, source = 'database') => 
    api.get(`/api/dashboard/recent-alerts?limit=${limit}&source=${source}`),
}

// Maps API
export const mapsAPI = {
  getLayers: () => api.get('/api/maps/layers'),
  getActiveIncidents: () => api.get('/api/maps/active-incidents'),
  getTimeEvolution: (incidentId: string) => api.get(`/api/maps/time-evolution?incident_id=${incidentId}`),
}

// Alerts API
export const alertsAPI = {
  getAlerts: (filters?: any) => api.get('/api/alerts/', { params: filters }),
  getSummary: () => api.get('/api/alerts/summary'),
  createAlert: (data: any) => api.post('/api/alerts/', data),
  updateAlert: (id: number, data: any) => api.patch(`/api/alerts/${id}`, data),
  markAllRead: () => api.post('/api/alerts/mark-all-read'),
  deleteAlert: (id: number) => api.delete(`/api/alerts/${id}`),
}

// Reports API
export const reportsAPI = {
  getReports: (filters?: any) => api.get('/api/reports/', { params: filters }),
  getSummary: () => api.get('/api/reports/summary'),
  createReport: (data: any) => api.post('/api/reports/', data),
  getReport: (reportId: string) => api.get(`/api/reports/${reportId}`),
  updateStatus: (reportId: string, status: string) =>
    api.patch(`/api/reports/${reportId}/status?status=${status}`),
  exportReport: (reportId: string, format = 'pdf') =>
    api.get(`/api/reports/${reportId}/export?format=${format}`),
}

// Settings API
export const settingsAPI = {
  getProfile: () => api.get('/api/settings/profile'),
  updateProfile: (data: any) => api.patch('/api/settings/profile', data),
  changePassword: (data: any) => api.post('/api/settings/change-password', data),
  getNotificationPreferences: () => api.get('/api/settings/notification-preferences'),
  updateNotificationPreferences: (data: any) =>
    api.patch('/api/settings/notification-preferences', data),
}

// Weather API
export const weatherAPI = {
  getCurrentWeather: (lat: number, lng: number) =>
    api.get(`/api/weather/current?latitude=${lat}&longitude=${lng}`),
  getForecast: (lat: number, lng: number, days = 7) =>
    api.get(`/api/weather/forecast?latitude=${lat}&longitude=${lng}&days=${days}`),
  getSevereAlerts: (lat: number, lng: number) =>
    api.get(`/api/weather/severe-weather?latitude=${lat}&longitude=${lng}`),
  getIndiaAlerts: () => api.get('/api/weather/india-alerts'),
  getTrafficIncidents: (lat: number, lng: number, radius = 50000) =>
    api.get(`/api/weather/traffic-incidents?latitude=${lat}&longitude=${lng}&radius=${radius}`),
  getIndiaTraffic: () => api.get('/api/weather/india-traffic'),
  getWeatherImpact: () => api.get('/api/weather/impact-analysis'),
}


export default api
