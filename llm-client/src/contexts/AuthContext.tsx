import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, User, LoginCredentials, RegisterCredentials } from '../services/auth.service'
import { storage } from '../utils/storage'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      try {
        const token = storage.getToken()
        if (token) {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
          storage.setUser(currentUser)
        }
      } catch (error) {
        console.error('Failed to get current user:', error)
        storage.clear()
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authService.login(credentials)
      setUser(response.user)
      toast.success('ログインしました')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'ログインに失敗しました')
      throw error
    }
  }

  const register = async (credentials: RegisterCredentials) => {
    try {
      const response = await authService.register(credentials)
      setUser(response.user)
      toast.success('アカウントを作成しました')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '登録に失敗しました')
      throw error
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
      setUser(null)
      toast.success('ログアウトしました')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
      storage.setUser(currentUser)
    } catch (error) {
      console.error('Failed to refresh user:', error)
      setUser(null)
      storage.clear()
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}