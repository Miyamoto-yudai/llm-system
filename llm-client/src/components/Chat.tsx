import React, { useState, useEffect, useRef, useMemo, memo } from 'react'
import clsx from 'clsx'
import { FaUser, FaPaperPlane, FaTrash, FaRedo, FaRobot, FaArrowDown } from 'react-icons/fa'
import { PlusIcon } from '@heroicons/react/24/outline'
import Dialog from './Dialog'
import ConversationSidebar from './ConversationSidebar'
import LoginModal from './LoginModal'
import LoadingSpinner from './LoadingSpinner'
import QuickTemplates from './QuickTemplates'
import TypingIndicator from './TypingIndicator'
import { useChatSocket } from '../useChatSocket'
import { useChatSocketAuth } from '../useChatSocketAuth'
import { useAuth } from '../contexts/AuthContext'
import { conversationService } from '../services/conversation.service'
import toast from 'react-hot-toast'


const StreamingMessage = memo(function StreamingMessage({chunk}: {chunk: string[]}) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const fullText = chunk.join('')

  useEffect(() => {
    // Reset when new message starts
    setDisplayedText('')
    setCurrentIndex(0)
  }, [])

  useEffect(() => {
    if (currentIndex < fullText.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + fullText[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, 20) // 20ms per character for smooth animation

      return () => clearTimeout(timer)
    }
  }, [currentIndex, fullText])

  if (chunk.length === 0) return null

  return (
    <div className='flex gap-2 animate-slideIn'>
      <div className='flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center'>
        <FaRobot className='text-sm' />
      </div>
      <div className='bg-gray-100 px-4 py-2 rounded-lg max-w-[70%]'>
        <span className='text-gray-800 whitespace-pre-wrap'>
          {displayedText}
          {currentIndex < fullText.length && (
            <span className='typing-cursor' />
          )}
        </span>
      </div>
    </div>
  )
})


const Chat: React.FC = () => {
  const { isAuthenticated, user } = useAuth()
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [isCreatingNewConversation, setIsCreatingNewConversation] = useState(false)
  const [isPendingNewConversation, setIsPendingNewConversation] = useState(false)

  // Use different hooks based on authentication status
  const guestChat = useChatSocket()
  const authChat = useChatSocketAuth(selectedConversationId)

  const chat = isAuthenticated ? authChat : guestChat
  const { inputText, setInputText, messages, onSubmit, chunk } = chat

  const [messageHistory, setMessageHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false)
  const [isComposing, setIsComposing] = useState(false)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lastMessageRef = useRef<string>('')
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Listen for new conversation creation from WebSocket
  useEffect(() => {
    const handleConversationCreated = (e: CustomEvent) => {
      if (isPendingNewConversation && e.detail?.conversationId) {
        setSelectedConversationId(e.detail.conversationId)
        setIsPendingNewConversation(false)
      }
    }

    window.addEventListener('conversationCreated', handleConversationCreated as any)
    return () => {
      window.removeEventListener('conversationCreated', handleConversationCreated as any)
    }
  }, [isPendingNewConversation])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+N: New conversation
      if (e.ctrlKey && e.key === 'n') {
        e.preventDefault()
        if (isAuthenticated) {
          handleNewConversation()
        }
      }
      // Ctrl+Shift+C: Clear chat
      if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        e.preventDefault()
        handleClearChat()
      }
      // Focus on input with '/'
      if (e.key === '/' && document.activeElement !== textareaRef.current) {
        e.preventDefault()
        textareaRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isAuthenticated])

  // Remove auto-scroll functionality - users can manually scroll as needed
  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior })
    setShowScrollButton(false)
  }

  // Check if user has scrolled up
  useEffect(() => {
    const container = messagesContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const threshold = 100
      const distanceFromBottom =
        container.scrollHeight - container.scrollTop - container.clientHeight

      setShowScrollButton(distanceFromBottom > threshold)
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  // Only scroll to bottom when user sends their own message
  const handleScrollOnUserMessage = () => {
    // Optional: scroll to bottom when user sends a message
    // Uncomment the line below if you want this behavior
    // scrollToBottom('smooth')
  }

  // Track when we're waiting for a response
  useEffect(() => {
    // When chunks arrive, we're no longer waiting
    if (chunk && chunk.length > 0) {
      setIsWaitingForResponse(false)
    }
  }, [chunk])

  // Reset waiting state when message is added to messages array
  useEffect(() => {
    // When a new bot message is added, we're done waiting
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.speakerId === 0) {
      setIsWaitingForResponse(false)
    }
  }, [messages])

  const handleSubmit = () => {
    if (inputText.trim()) {
      // Add to history
      setMessageHistory(prev => [...prev, inputText])
      lastMessageRef.current = inputText
      setHistoryIndex(-1)
      // Set waiting flag when submitting
      setIsWaitingForResponse(true)
      onSubmit()
      // Optional: scroll after sending message
      handleScrollOnUserMessage()
    }
  }

  const handleHistoryNavigation = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp' && !e.shiftKey) {
      e.preventDefault()
      if (historyIndex < messageHistory.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setInputText(messageHistory[messageHistory.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown' && !e.shiftKey) {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setInputText(messageHistory[messageHistory.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setInputText('')
      }
    }
  }

  const handleClearChat = () => {
    if ('resetChat' in chat && typeof (chat as any).resetChat === 'function') {
      (chat as any).resetChat()
      toast.success('会話をクリアしました')
    }
  }

  const handleResendLastMessage = () => {
    if (lastMessageRef.current) {
      setInputText(lastMessageRef.current)
      setTimeout(() => handleSubmit(), 100)
    }
  }

  const handleTemplateSelect = (template: string) => {
    setInputText(template)
    textareaRef.current?.focus()
  }

  // Memoize the messages for Dialog to prevent re-renders on input changes
  const dialogMessages = useMemo(() => {
    return messages.map((msg, idx) => ({
      ...msg,
      isAnimated: idx === messages.length - 1 && msg.speakerId === 0
    }))
  }, [messages])

  const handleNewConversation = async () => {
    if (!isAuthenticated) return

    // Reset to null to indicate new conversation (won't be saved until first message)
    setSelectedConversationId(null)
    setIsPendingNewConversation(true)
    if ('resetChat' in chat) {
      (chat as any).resetChat()
    }
    toast.success('新しい会話を開始しました')
  }

  return (
    <div className='flex h-full w-full min-h-screen'>
      {/* Sidebar for authenticated users */}
      {isAuthenticated && (
        <ConversationSidebar
          selectedConversationId={selectedConversationId}
          onSelectConversation={setSelectedConversationId}
          onNewConversation={handleNewConversation}
        />
      )}

      {/* Main chat area */}
      <div className='flex flex-col flex-1 h-full w-full items-center bg-gray-50'>
        {/* Login prompt for guests */}
        {!isAuthenticated && (
          <div className='bg-blue-50 border-b border-blue-200 p-3 w-full'>
            <div className='max-w-screen-md mx-auto flex items-center justify-between'>
              <div className='flex items-center space-x-2 text-sm text-gray-700'>
                <FaUser className='text-blue-600' />
                <span>ゲストとして利用中です。ログインすると会話履歴が保存されます。</span>
              </div>
              <button
                onClick={() => setIsLoginModalOpen(true)}
                className='px-4 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors'
              >
                ログイン / 新規登録
              </button>
            </div>
          </div>
        )}

        <div className='flex flex-col justify-center w-full max-w-screen-lg gap-5 p-5'>
          {isCreatingNewConversation ? (
            <LoadingSpinner />
          ) : (
            <>
              {/* Messages area */}
              <div className='relative'>
                <div
                  ref={messagesContainerRef}
                  className='bg-white border border-gray-200 rounded-lg p-4 min-h-[400px] max-h-[600px] overflow-y-auto'
                >
                {messages.length === 0 ? (
                  <div className='flex flex-col items-center justify-center h-64 text-gray-500'>
                    <div className='text-5xl mb-4'>⚖️</div>
                    <h3 className='text-lg font-semibold mb-2 text-gray-700'>法律相談チャットボット</h3>
                    <p className='text-sm text-gray-600'>お困りのことについて、お気軽にご相談ください</p>
                  </div>
                ) : (
                  <>
                    <Dialog messages={dialogMessages} />
                    {/* Show typing indicator only when waiting for response and no chunks yet */}
                    {isWaitingForResponse && (!chunk || chunk.length === 0) && (
                      <TypingIndicator />
                    )}
                    {/* Show streaming message as it arrives */}
                    {chunk && chunk.length > 0 && (
                      <StreamingMessage chunk={chunk} />
                    )}
                  </>
                )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Scroll to bottom button */}
                {showScrollButton && (
                  <button
                    onClick={() => scrollToBottom('smooth')}
                    className='absolute bottom-4 right-4 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all transform hover:scale-110'
                    title='最新メッセージへ移動'
                  >
                    <FaArrowDown className='w-4 h-4' />
                  </button>
                )}
              </div>

              {/* Quick actions bar */}
              <div className='flex flex-wrap gap-2 items-center'>
                <QuickTemplates onSelectTemplate={handleTemplateSelect} />

                <div className='flex gap-2 ml-auto'>
                  {messages.length > 0 && (
                    <>
                      <button
                        onClick={handleResendLastMessage}
                        className='flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded hover:bg-gray-50 transition-colors'
                        title='前回の質問を再送信 (↑キー)'
                      >
                        <FaRedo className='w-3 h-3 text-gray-600' />
                        <span className='hidden sm:inline text-gray-700'>再送信</span>
                      </button>
                      <button
                        onClick={handleClearChat}
                        className='flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded hover:bg-gray-50 transition-colors text-gray-600 hover:text-red-600'
                        title='会話をクリア (Ctrl+Shift+C)'
                      >
                        <FaTrash className='w-3 h-3' />
                        <span className='hidden sm:inline'>クリア</span>
                      </button>
                    </>
                  )}
                  {isAuthenticated && (
                    <button
                      onClick={handleNewConversation}
                      className='flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors'
                      title='新しい会話 (Ctrl+N)'
                    >
                      <PlusIcon className='w-4 h-4' />
                      <span className='hidden sm:inline'>新しい会話</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Input area */}
              <div className={clsx(
                'bg-white border rounded-lg p-4 transition-colors',
                isComposing ? 'border-yellow-400 bg-yellow-50/30' : 'border-gray-200'
              )}>
                <div className='flex gap-3'>
                  <textarea
                    ref={textareaRef}
                    className='flex-1 resize-none outline-none text-gray-800 placeholder-gray-400 min-h-[60px] max-h-[200px] focus:outline-none'
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onCompositionStart={() => setIsComposing(true)}
                    onCompositionEnd={() => setIsComposing(false)}
                    onKeyDown={(e) => {
                      // Don't submit if we're composing (Japanese input)
                      if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
                        e.preventDefault()
                        handleSubmit()
                      } else {
                        handleHistoryNavigation(e)
                      }
                    }}
                    placeholder='質問を入力してください...'
                    rows={2}
                  />
                  <button
                    onClick={handleSubmit}
                    disabled={!inputText.trim()}
                    className={clsx(
                      'self-end px-4 py-2 rounded font-medium transition-colors',
                      'flex items-center gap-2',
                      inputText.trim()
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    )}
                  >
                    <FaPaperPlane className='w-4 h-4' />
                    <span>送信</span>
                  </button>
                </div>

                {/* Keyboard shortcuts hint */}
                <div className='mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-3 text-xs text-gray-500'>
                  <span>Enter: 送信 {isComposing && '(変換中)'}</span>
                  <span>Shift+Enter: 改行</span>
                  <span>↑/↓: 履歴</span>
                  <span>/: 入力にフォーカス</span>
                  {isAuthenticated && <span>Ctrl+N: 新規会話</span>}
                  <span>Ctrl+Shift+C: クリア</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />
    </div>
  )}

export default Chat
