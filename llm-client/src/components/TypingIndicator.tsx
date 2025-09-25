import React, { memo } from 'react'
import { FaRobot } from 'react-icons/fa'

const TypingIndicator: React.FC = memo(() => {
  return (
    <div className='flex gap-2 animate-slideIn'>
      <div className='flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center'>
        <FaRobot className='text-sm' />
      </div>
      <div className='bg-gray-100 rounded-lg'>
        <div className='typing-indicator'>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  )
})

export default TypingIndicator