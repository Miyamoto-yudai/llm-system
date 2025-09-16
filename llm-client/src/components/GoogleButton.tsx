import React from 'react'
import { FaGoogle } from 'react-icons/fa'

interface GoogleButtonProps {
  onClick: () => void
  isLoading?: boolean
  text?: string
}

const GoogleButton: React.FC<GoogleButtonProps> = ({
  onClick,
  isLoading = false,
  text = 'Googleで続ける'
}) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="w-full flex items-center justify-center space-x-3 px-4 py-3 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <FaGoogle className="text-xl" style={{ color: '#4285F4' }} />
      <span className="text-gray-700 font-medium">
        {isLoading ? '処理中...' : text}
      </span>
    </button>
  )
}

export default GoogleButton