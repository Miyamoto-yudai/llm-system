import React, { useState, useEffect } from 'react'
import clsx from 'clsx'
import { FaUser } from 'react-icons/fa'
import Button from './Button'
import Dialog from './Dialog'
import ConversationSidebar from './ConversationSidebar'
import LoginModal from './LoginModal'
import LoadingSpinner from './LoadingSpinner'
import { useChatSocket } from '../useChatSocket'
import { useChatSocketAuth } from '../useChatSocketAuth'
import { useAuth } from '../contexts/AuthContext'
import { conversationService } from '../services/conversation.service'
import toast from 'react-hot-toast'


function PseudoUtt({chunk}: {chunk: string[]}) {
  return (
    <div>
    {chunk.length > 0 &&
     <ul className=' flex flex-col h-full w-full gap-2'>
      <li className={clsx(
        'flex ','justify-start'
      )}>
      <div
      className={clsx(
        'relative max-w-[80%] px-4 py-2  rounded shadow'
      )}
      >
      <span className='block'>{chunk.join('')}</span>
    </div>
    </li>
    </ul>}
    </div>
)}


const Chat: React.FC = () => {
  const { isAuthenticated, user } = useAuth()
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [isCreatingNewConversation, setIsCreatingNewConversation] = useState(false)

  // Use different hooks based on authentication status
  const guestChat = useChatSocket()
  const authChat = useChatSocketAuth(selectedConversationId)

  const chat = isAuthenticated ? authChat : guestChat
  const { inputText, setInputText, messages, onSubmit, chunk } = chat

  const onSubmitWithInputText1 = () => {
    setInputText("どのような罪になるか知りたい");
  }
  const onSubmitWithInputText2 = () => {
    setInputText("警察に相談したらいいのかわからない");
  }

  const handleNewConversation = async () => {
    if (!isAuthenticated) return

    setIsCreatingNewConversation(true)
    try {
      const newConv = await conversationService.createConversation({
        title: '新しい会話'
      })
      setSelectedConversationId(newConv.id)
      if ('resetChat' in chat) {
        (chat as any).resetChat()
      }
      toast.success('新しい会話を開始しました')
    } catch (error) {
      toast.error('会話の作成に失敗しました')
    } finally {
      setIsCreatingNewConversation(false)
    }
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
      <div className='flex flex-col flex-1 h-full w-full items-center'>
        {/* Login prompt for guests */}
        {!isAuthenticated && (
          <div className='bg-blue-50 border-b border-blue-200 p-3 w-full'>
            <div className='max-w-screen-md mx-auto flex items-center justify-between'>
              <div className='flex items-center space-x-2 text-sm text-blue-800'>
                <FaUser />
                <span>ゲストとして利用中です。ログインすると会話履歴が保存されます。</span>
              </div>
              <button
                onClick={() => setIsLoginModalOpen(true)}
                className='px-4 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 transition-colors'
              >
                ログイン / 新規登録
              </button>
            </div>
          </div>
        )}

        <div
          className={clsx(
            'flex flex-col justify-center w-5/6 max-w-screen-md gap-5 p-5'
          )}
        >
          {isCreatingNewConversation ? (
            <LoadingSpinner />
          ) : (
            <>
              <Dialog messages={messages} />
              <PseudoUtt chunk={chunk} />
              <div id='input_form' className={clsx('flex flex-row gap-3')}>
                <textarea
                  className='w-full border rounded-md p-2'
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      onSubmit()
                    }
                  }}
                  placeholder='質問を入力してください...'
                />
                <Button onClick={onSubmit} label='送信'/>
              </div>
              <div className='flex flex-col sm:flex-row gap-3'>
                <Button onClick={onSubmitWithInputText1} label='どのような罪になるか知りたい'/>
                <Button onClick={onSubmitWithInputText2} label='警察に相談したらいいのかわからない'/>
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