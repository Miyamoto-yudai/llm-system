import axios from 'axios'
import { storage } from '../utils/storage'

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080'

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = storage.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear storage and redirect to login
      storage.clear()
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export const getWebSocketUrl = (endpoint: string, params?: Record<string, string>) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsHost = API_BASE_URL.replace(/^https?:/, wsProtocol)
  const queryParams = params ? '?' + new URLSearchParams(params).toString() : ''
  return `${wsHost}${endpoint}${queryParams}`
}