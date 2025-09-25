import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { FaFlask } from 'react-icons/fa'
import { useAuth } from '../contexts/AuthContext'
import UserMenu from './UserMenu'

const Header: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  const isComparisonModeEnabled = import.meta.env.VITE_COMPARISON_MODE_ENABLED === 'true'
  const isOnComparisonPage = location.pathname === '/comparison'

  return (
    <header className='bg-white border-b border-gray-200 w-full'>
      <div className='container mx-auto px-4'>
        <div className='flex justify-between items-center h-16'>
          <a href="/" className='flex items-center gap-2'>
            <div className='w-8 h-8 bg-blue-600 rounded flex items-center justify-center'>
              <span className='text-white text-sm font-bold'>⚖️</span>
            </div>
            <div className='flex flex-col'>
              <h1 className='text-xl font-bold text-gray-900'>
                LawFlow
              </h1>
              <span className='text-xs text-gray-500 -mt-1'>法律相談チャットボット</span>
            </div>
          </a>

          <div className='flex items-center gap-4'>
            {/* Comparison mode toggle button (development only) */}
            {isComparisonModeEnabled && !isOnComparisonPage && (
              <Link
                to="/comparison"
                className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                title="深掘り質問の比較検証モード"
              >
                <FaFlask className="w-3 h-3" />
                <span>比較モード</span>
              </Link>
            )}

            <a href="https://tokyo-keijibengosi.com/"
               target="_blank"
               rel="noopener noreferrer"
               className="hidden md:flex flex-col items-end text-gray-600 hover:text-blue-600 transition-colors">
              <span className="text-xs text-gray-500">協力弁護士</span>
              <span className="text-sm">弁護士法人あいち刑事事件総合法律事務所</span>
            </a>

            {isAuthenticated && <UserMenu />}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
