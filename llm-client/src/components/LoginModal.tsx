import React, { useState } from 'react'
import { FaTimes, FaEnvelope, FaLock, FaUser } from 'react-icons/fa'
import { useAuth } from '../contexts/AuthContext'
import { oauthService } from '../services/oauth.service'
import GoogleButton from './GoogleButton'
import clsx from 'clsx'

interface LoginModalProps {
  isOpen: boolean
  onClose: () => void
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { login, register } = useAuth()
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!isOpen) return null

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.email) {
      newErrors.email = 'メールアドレスは必須です'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = '有効なメールアドレスを入力してください'
    }

    if (!formData.password) {
      newErrors.password = 'パスワードは必須です'
    } else if (formData.password.length < 8) {
      newErrors.password = 'パスワードは8文字以上である必要があります'
    }

    if (!isLoginMode) {
      if (!formData.username) {
        newErrors.username = 'ユーザー名は必須です'
      } else if (formData.username.length < 3) {
        newErrors.username = 'ユーザー名は3文字以上である必要があります'
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'パスワードが一致しません'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setIsLoading(true)
    try {
      if (isLoginMode) {
        await login({
          email: formData.email,
          password: formData.password
        })
      } else {
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
      }
      onClose()
      setFormData({ username: '', email: '', password: '', confirmPassword: '' })
    } catch (error) {
      // Error handling is done in AuthContext
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true)
    try {
      oauthService.initiateGoogleLogin()
    } catch (error) {
      console.error('Google login error:', error)
      setIsGoogleLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const switchMode = () => {
    setIsLoginMode(!isLoginMode)
    setErrors({})
    setFormData({ username: '', email: '', password: '', confirmPassword: '' })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <FaTimes size={24} />
        </button>

        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {isLoginMode ? 'ログイン' : 'アカウント作成'}
          </h2>
          <p className="text-gray-600 text-sm">
            {isLoginMode
              ? 'アカウントにログインして続ける'
              : '新しいアカウントを作成して始める'}
          </p>
        </div>

        {/* Google Login Button */}
        <div className="mb-6">
          <GoogleButton
            onClick={handleGoogleLogin}
            isLoading={isGoogleLoading}
            text={isLoginMode ? 'Googleでログイン' : 'Googleで登録'}
          />
        </div>

        {/* Divider */}
        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-white text-gray-500">または</span>
          </div>
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLoginMode && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <div className="flex items-center space-x-2">
                  <FaUser className="text-gray-400" />
                  <span>ユーザー名</span>
                </div>
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className={clsx(
                  'w-full px-4 py-3 border-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                  errors.username ? 'border-red-500' : 'border-gray-300 hover:border-gray-400'
                )}
                placeholder="山田太郎"
              />
              {errors.username && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <span>⚠️ {errors.username}</span>
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <div className="flex items-center space-x-2">
                <FaEnvelope className="text-gray-400" />
                <span>メールアドレス</span>
              </div>
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={clsx(
                'w-full px-4 py-3 border-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                errors.email ? 'border-red-500' : 'border-gray-300 hover:border-gray-400'
              )}
              placeholder="example@email.com"
            />
            {errors.email && (
              <p className="mt-2 text-sm text-red-600 flex items-center">
                <span>⚠️ {errors.email}</span>
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <div className="flex items-center space-x-2">
                <FaLock className="text-gray-400" />
                <span>パスワード</span>
              </div>
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={clsx(
                'w-full px-4 py-3 border-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                errors.password ? 'border-red-500' : 'border-gray-300 hover:border-gray-400'
              )}
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-2 text-sm text-red-600 flex items-center">
                <span>⚠️ {errors.password}</span>
              </p>
            )}
          </div>

          {!isLoginMode && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                <div className="flex items-center space-x-2">
                  <FaLock className="text-gray-400" />
                  <span>パスワード（確認）</span>
                </div>
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={clsx(
                  'w-full px-4 py-3 border-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300 hover:border-gray-400'
                )}
                placeholder="••••••••"
              />
              {errors.confirmPassword && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <span>⚠️ {errors.confirmPassword}</span>
                </p>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className={clsx(
              'w-full py-3 px-4 rounded-lg text-white font-semibold transition-all duration-200 transform',
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg active:scale-[0.98]'
            )}
          >
            {isLoading ? '処理中...' : isLoginMode ? 'ログイン' : 'アカウント作成'}
          </button>
        </form>

        {/* Switch Mode Link */}
        <div className="mt-6 text-center">
          <button
            onClick={switchMode}
            className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
          >
            {isLoginMode
              ? 'アカウントをお持ちでない方はこちら →'
              : 'すでにアカウントをお持ちの方はこちら →'}
          </button>
        </div>

        {/* Footer Info */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center space-y-1">
            <p>✅ ログインすると会話履歴が自動保存されます</p>
            <p>✅ いつでもゲストとして利用可能です</p>
            <p>✅ Googleアカウントで簡単ログイン</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginModal