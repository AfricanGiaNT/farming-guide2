import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.VITE_API_BASE_URL || '/api',
  timeout: 15000, // 15 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Weather API endpoints
export const weatherAPI = {
  getCurrentWeather: async (lat: number, lon: number) => {
    const response = await api.get(`/weather/${lat}/${lon}`)
    return response.data
  },

  getWeatherForecast: async (lat: number, lon: number) => {
    const response = await api.get(`/weather/${lat}/${lon}/forecast`)
    return response.data
  },

  getRainfallData: async (lat: number, lon: number) => {
    const response = await api.get(`/rainfall/${lat}/${lon}`)
    return response.data
  },

  getHistoricalWeather: async (lat: number, lon: number, years: number = 5) => {
    const response = await api.get(`/weather/${lat}/${lon}/historical?years=${years}`)
    return response.data
  },
}

// Crop API endpoints
export const cropAPI = {
  getCropRecommendations: async (
    lat: number, 
    lon: number, 
    season: 'current' | 'rainy' | 'dry' | 'all' = 'current'
  ) => {
    const response = await api.get(`/crops?location=${lat},${lon}&season=${season}`)
    return response.data
  },

  getSpecificCropRecommendations: async (
    cropName: string,
    lat: number,
    lon: number,
    season: 'current' | 'rainy' | 'dry' | 'all' = 'current'
  ) => {
    const response = await api.get(`/crops/specific?crop=${cropName}&location=${lat},${lon}&season=${season}`)
    return response.data
  },

  getVarietyInformation: async (cropName: string, lat?: number, lon?: number) => {
    const params = new URLSearchParams()
    if (lat && lon) {
      params.append('lat', lat.toString())
      params.append('lon', lon.toString())
    }
    const queryString = params.toString()
    const url = `/varieties/${cropName}${queryString ? `?${queryString}` : ''}`
    const response = await api.get(url)
    return response.data
  },

  getPlantingCalendar: async (cropName: string, lat: number, lon: number) => {
    const response = await api.get(`/planting-calendar/${cropName}/${lat}/${lon}`)
    return response.data
  },

  getYieldPrediction: async (cropName: string, lat: number, lon: number) => {
    const response = await api.get(`/yield-prediction/${cropName}/${lat}/${lon}`)
    return response.data
  },
}

// Knowledge Base API endpoints
export const knowledgeAPI = {
  searchDocuments: async (
    query: string, 
    filters?: {
      category?: string
      qualityScore?: number
      dateRange?: { start: string; end: string }
    },
    page: number = 1,
    limit: number = 10
  ) => {
    const response = await api.post('/search', {
      query,
      filters,
      page,
      limit,
    })
    return response.data
  },

  getCategories: async () => {
    const response = await api.get('/search/categories')
    return response.data
  },

  getDocument: async (documentId: string) => {
    const response = await api.get(`/documents/${documentId}`)
    return response.data
  },
}

// User feedback API endpoints
export const feedbackAPI = {
  submitFeedback: async (feedback: {
    type: 'rating' | 'comment' | 'helpful' | 'report'
    contentId: string
    value: any
    comment?: string
  }) => {
    const response = await api.post('/feedback', feedback)
    return response.data
  },

  getFeedbackSummary: async () => {
    const response = await api.get('/feedback/summary')
    return response.data
  },
}

// Analytics API endpoints
export const analyticsAPI = {
  getDashboardData: async () => {
    const response = await api.get('/analytics/dashboard')
    return response.data
  },

  getUsageMetrics: async (period: '7d' | '30d' | '90d' = '30d') => {
    const response = await api.get(`/analytics/usage?period=${period}`)
    return response.data
  },
}

export default api