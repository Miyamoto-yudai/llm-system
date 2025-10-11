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

// Pydantic v2エラーフォーマット用のヘルパー関数
interface PydanticError {
  type: string
  loc: (string | number)[]
  msg: string
  input?: any
  ctx?: Record<string, any>
}

function formatPydanticError(detail: string | PydanticError[] | undefined): string {
  if (!detail) return '不明なエラーが発生しました'

  // 文字列の場合はそのまま返す（Pydantic v1互換）
  if (typeof detail === 'string') return detail

  // 配列の場合はPydantic v2のエラー形式
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map(err => {
      const field = err.loc.slice(1).join('.') // ['body', 'password'] -> 'password'
      return field ? `${field}: ${err.msg}` : err.msg
    }).join(', ')
  }

  return 'バリデーションエラーが発生しました'
}

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
      const errorMessage = formatPydanticError(error.response?.data?.detail) || 'ログインに失敗しました'
      toast.error(errorMessage)
      throw error
    }
  }

  const register = async (credentials: RegisterCredentials) => {
    try {
      console.log('🔵 Registration attempt:', { username: credentials.username, email: credentials.email, password: '[REDACTED]' })
      const response = await authService.register(credentials)
      console.log('✅ Registration success:', response.user)
      setUser(response.user)
      toast.success('アカウントを作成しました')
    } catch (error: any) {
      console.error('❌ Registration error:', {
        status: error.response?.status,
        detail: error.response?.data?.detail,
        fullError: error.response?.data
      })
      const errorMessage = formatPydanticError(error.response?.data?.detail) || '登録に失敗しました'
      console.log('📝 Formatted error message:', errorMessage)
      toast.error(errorMessage)
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