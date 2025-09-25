import { api } from './api.config'
import { storage } from '../utils/storage'

export interface User {
  id: string
  username: string
  email: string
  created_at: string
  is_active: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export const authService = {
  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/register', credentials)
    const data = response.data
    storage.setToken(data.access_token)
    storage.setUser(data.user)
    return data
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/login', credentials)
    const data = response.data
    storage.setToken(data.access_token)
    storage.setUser(data.user)
    return data
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout')
    } finally {
      storage.clear()
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/api/auth/me')
    return response.data
  },

  async deleteAccount(): Promise<void> {
    await api.delete('/api/auth/account')
    storage.clear()
  },

  isAuthenticated(): boolean {
    return !!storage.getToken()
  }
}