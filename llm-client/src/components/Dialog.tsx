import clsx from 'clsx'
import React, { useEffect, useState, memo } from 'react'
import { FaUser, FaRobot } from 'react-icons/fa'

export type DialogProps = {
  messages: Message[]
  isTyping?: boolean
}
export type Message = {
  speakerId: number
  text: string
  timestamp?: Date
  isAnimated?: boolean
}

const Dialog = memo(function Dialog({ messages, isTyping = false }: DialogProps) {
  const formatTime = (date?: Date) => {
    if (!date) return ''
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return '今'
    if (minutes < 60) return `${minutes}分前`
    if (minutes < 1440) return `${Math.floor(minutes / 60)}時間前`
    return date.toLocaleDateString('ja-JP')
  }

  const AnimatedText = memo<{ text: string; animate: boolean; isAssistant: boolean }>(({
    text,
    animate,
    isAssistant
  }) => {
    const [displayedText, setDisplayedText] = useState(animate ? '' : text)
    const [isAnimating, setIsAnimating] = useState(animate)

    useEffect(() => {
      if (!animate) {
        setDisplayedText(text)
        setIsAnimating(false)
        return
      }

      setDisplayedText('')
      setIsAnimating(true)

      let currentIndex = 0
      const totalLength = text.length

      if (totalLength === 0) {
        setIsAnimating(false)
        return
      }

      const step = () => {
        currentIndex += 1
        setDisplayedText(text.slice(0, currentIndex))

        if (currentIndex >= totalLength) {
          setIsAnimating(false)
          return
        }

        timer = window.setTimeout(step, 18)
      }

      let timer = window.setTimeout(step, 18)

      return () => window.clearTimeout(timer)
    }, [text, animate])

    return (
      <span
        className={clsx(
          'whitespace-pre-wrap break-words',
          isAssistant ? 'text-gray-800' : 'text-white'
        )}
      >
        {displayedText}
        {isAnimating && <span className='typing-cursor' />}
      </span>
    )
  })

  return (
    <div className='flex flex-col h-full w-full gap-3 py-4'>
      {messages.map((message, index) => {
        const isLastMessage = index === messages.length - 1
        const shouldAnimate = Boolean(message.isAnimated && message.speakerId === 0)

        return (
          <div
            key={`${message.text}-${index}`}
            className={clsx(
              'flex gap-2',
              shouldAnimate ? 'animate-slideIn' : 'animate-fadeIn',
              message.speakerId === 0 ? 'flex-row' : 'flex-row-reverse'
            )}
          >
            {/* Avatar */}
            <div className={clsx(
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
              message.speakerId === 0
                ? 'bg-blue-100 text-blue-600'
                : 'bg-gray-100 text-gray-600'
            )}>
              {message.speakerId === 0 ? (
                <FaRobot className='text-sm' />
              ) : (
                <FaUser className='text-sm' />
              )}
            </div>

            {/* Message content */}
            <div className={clsx(
              'flex flex-col gap-1 max-w-[70%]',
              message.speakerId === 0 ? 'items-start' : 'items-end'
            )}>
              <div
                className={clsx(
                  'px-4 py-2 rounded-lg',
                  message.speakerId === 0
                    ? 'bg-gray-100 text-gray-800'
                    : 'bg-blue-600 text-white',
                )}
              >
                <AnimatedText
                  text={message.text}
                  animate={shouldAnimate}
                  isAssistant={message.speakerId === 0}
                />
              </div>

              {/* Timestamp */}
              {message.timestamp && (
                <span className='text-xs text-gray-400 px-2'>
                  {formatTime(message.timestamp)}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
})

export default Dialog
