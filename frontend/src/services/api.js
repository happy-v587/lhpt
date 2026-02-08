import axios from 'axios'

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    console.log('API Request:', config.method?.toUpperCase(), config.baseURL + config.url)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.config.url, response.status)
    // 返回 response.data 而不是整个 response
    return response.data
  },
  error => {
    const message = error.response?.data?.detail || 
                    error.response?.data?.error?.message || 
                    error.message || 
                    '请求失败'
    console.error('API Error:', error.config?.url, message, error.response?.data)
    return Promise.reject(error)
  }
)

export default apiClient
