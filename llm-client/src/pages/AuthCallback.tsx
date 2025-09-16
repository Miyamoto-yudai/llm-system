import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { storage } from '../utils/storage'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

const AuthCallback: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { refreshUser } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      const token = searchParams.get('token')
      const error = searchParams.get('message')

      if (error) {
        toast.error('認証に失敗しました: ' + error)
        navigate('/')
        return
      }

      if (token) {
        // Store the token
        storage.setToken(token)

        try {
          // Refresh user info
          await refreshUser()
          toast.success('ログインしました')
          navigate('/')
        } catch (error) {
          console.error('Failed to get user info:', error)
          toast.error('ユーザー情報の取得に失敗しました')
          navigate('/')
        }
      } else {
        toast.error('認証トークンが見つかりません')
        navigate('/')
      }
    }

    handleCallback()
  }, [searchParams, navigate, refreshUser])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">認証処理中...</p>
        <p className="text-sm text-gray-500 mt-2">しばらくお待ちください</p>
      </div>
    </div>
  )
}

export default AuthCallback