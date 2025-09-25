import React, { useState, useRef, useEffect } from 'react'
import { FaUser, FaSignOutAlt, FaCog } from 'react-icons/fa'
import { useAuth } from '../contexts/AuthContext'
import clsx from 'clsx'

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!user) return null

  const handleLogout = async () => {
    await logout()
    setIsOpen(false)
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-md bg-gray-800 hover:bg-gray-700 transition-colors"
      >
        <FaUser className="text-white" />
        <span className="text-white font-medium">{user.username}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200 z-50">
          <div className="p-4 border-b border-gray-200">
            <p className="font-semibold text-gray-900">{user.username}</p>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>

          <div className="py-2">
            <button
              onClick={() => {
                // TODO: 設定画面の実装
                setIsOpen(false)
              }}
              className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
            >
              <FaCog />
              <span>設定</span>
            </button>

            <button
              onClick={handleLogout}
              className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center space-x-3"
            >
              <FaSignOutAlt />
              <span>ログアウト</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserMenu