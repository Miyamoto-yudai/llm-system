import React, { useRef, useEffect } from 'react'
import { FaRobot, FaUser } from 'react-icons/fa'
import TypingIndicator from './TypingIndicator'

interface Message {
  speakerId: number
  text: string
  timestamp?: number
}

interface ComparisonChatProps {
  title: string
  messages: Message[]
  chunks: string[]
  isProcessing: boolean
  variant: 'with-data' | 'without-data' | 'with-rag' | 'without-rag'
  subtitle?: string  // オプショナルなサブタイトル
}

const ComparisonChat: React.FC<ComparisonChatProps> = ({
  title,
  messages,
  chunks,
  isProcessing,
  variant,
  subtitle
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chunks])

  const isWithVariant = variant === 'with-data' || variant === 'with-rag'
  const bgColor = isWithVariant ? 'bg-blue-50' : 'bg-green-50'
  const borderColor = isWithVariant ? 'border-blue-200' : 'border-green-200'
  const titleBgColor = isWithVariant ? 'bg-blue-600' : 'bg-green-600'
  const assistantBgColor = isWithVariant ? 'bg-blue-100' : 'bg-green-100'
  const assistantIconColor = isWithVariant ? 'text-blue-600' : 'text-green-600'

  // デフォルトのサブタイトル（指定されていない場合）
  const defaultSubtitle = variant === 'with-data'
    ? '罪名予測テーブル・量刑予測シート使用'
    : variant === 'without-data'
    ? 'LLMプロンプトのみ使用'
    : ''  // RAGモードではサブタイトルなし

  return (
    <div className={`flex flex-col h-full ${bgColor} rounded-lg border ${borderColor} overflow-hidden`}>
      {/* Header */}
      <div className={`${titleBgColor} text-white px-4 py-3`}>
        <h3 className="font-semibold text-lg">{title}</h3>
        {(subtitle !== undefined ? subtitle : defaultSubtitle) && (
          <p className="text-sm opacity-90 mt-1">
            {subtitle !== undefined ? subtitle : defaultSubtitle}
          </p>
        )}
      </div>

      {/* Messages */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto p-4 space-y-3"
      >
        {messages.length === 0 && !isProcessing ? (
          <div className="text-center text-gray-500 mt-8">
            <p>メッセージがありません</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-2 ${
                  message.speakerId === 1 ? 'justify-end' : 'justify-start'
                } animate-slideIn`}
              >
                {message.speakerId === 0 && (
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full ${assistantBgColor} ${assistantIconColor} flex items-center justify-center`}>
                    <FaRobot className="text-sm" />
                  </div>
                )}
                <div
                  className={`px-4 py-2 rounded-lg max-w-[80%] ${
                    message.speakerId === 1
                      ? 'bg-gray-700 text-white'
                      : `${assistantBgColor} text-gray-800`
                  }`}
                >
                  <span className="whitespace-pre-wrap">{message.text}</span>
                  {message.timestamp && (
                    <div className="text-xs opacity-60 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString('ja-JP')}
                    </div>
                  )}
                </div>
                {message.speakerId === 1 && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 text-white flex items-center justify-center">
                    <FaUser className="text-sm" />
                  </div>
                )}
              </div>
            ))}

            {/* Show typing indicator when processing but no chunks yet */}
            {isProcessing && chunks.length === 0 && (
              <TypingIndicator />
            )}

            {/* Show streaming chunks */}
            {chunks.length > 0 && (
              <div className="flex gap-2 animate-slideIn">
                <div className={`flex-shrink-0 w-8 h-8 rounded-full ${assistantBgColor} ${assistantIconColor} flex items-center justify-center`}>
                  <FaRobot className="text-sm" />
                </div>
                <div className={`${assistantBgColor} px-4 py-2 rounded-lg max-w-[80%]`}>
                  <span className="text-gray-800 whitespace-pre-wrap">
                    {chunks.join('')}
                    <span className="typing-cursor" />
                  </span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Statistics */}
      <div className={`border-t ${borderColor} px-4 py-2 text-sm text-gray-600`}>
        <div className="flex justify-between">
          <span>メッセージ数: {messages.length}</span>
          <span>
            深掘り質問: {
              messages.filter(m =>
                m.speakerId === 0 && m.text.includes('【確認ステップ')
              ).length
            }回
          </span>
        </div>
      </div>
    </div>
  )
}

export default ComparisonChat