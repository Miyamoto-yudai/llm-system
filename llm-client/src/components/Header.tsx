import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import UserMenu from './UserMenu'

const Header: React.FC = () => {
  const { isAuthenticated } = useAuth()
  return (
    <header className='bg-gray-900 py-6 w-full '>
      <div className='container mx-auto px-4 flex justify-between items-center'>
        <a href="/">
          <h3 className='text-white text-3xl font-bold'>法律相談LawFlow</h3>
        </a>

        <div className='flex items-center space-x-6'>
          <a href="https://tokyo-keijibengosi.com/"
             target="_blank"
             className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">
            <h3 className="text-right text-lg font-bold text-white">協力弁護士</h3>
            <p>弁護士法人あいち刑事事件総合法律事務所</p>
          </a>

          {isAuthenticated && <UserMenu />}
        </div>
      </div>
    </header>
    )
}

export default Header
