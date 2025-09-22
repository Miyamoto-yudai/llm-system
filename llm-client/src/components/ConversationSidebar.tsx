import React, { useState, useEffect } from 'react'
import { FaPlus, FaTrash, FaEdit, FaComments, FaBars, FaTimes } from 'react-icons/fa'
import { conversationService, Conversation } from '../services/conversation.service'
import { useAuth } from '../contexts/AuthContext'
import clsx from 'clsx'
import toast from 'react-hot-toast'

interface ConversationSidebarProps {
  selectedConversationId: string | null
  onSelectConversation: (id: string | null) => void
  onNewConversation: () => void
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  selectedConversationId,
  onSelectConversation,
  onNewConversation
}) => {
  const { isAuthenticated } = useAuth()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      loadConversations()
    }
  }, [isAuthenticated])

  const loadConversations = async () => {
    setIsLoading(true)
    try {
      const data = await conversationService.getConversations(0, 50)
      setConversations(data)
    } catch (error) {
      console.error('Failed to load conversations:', error)
      toast.error('会話履歴の読み込みに失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteConversation = async (id: string) => {
    if (!window.confirm('この会話を削除してもよろしいですか？')) return

    try {
      await conversationService.deleteConversation(id)
      setConversations(prev => prev.filter(c => c.id !== id))
      if (selectedConversationId === id) {
        onSelectConversation(null)
      }
      toast.success('会話を削除しました')
    } catch (error) {
      toast.error('削除に失敗しました')
    }
  }

  const handleEditTitle = async (id: string) => {
    if (!editingTitle.trim()) return

    try {
      await conversationService.updateConversationTitle(id, editingTitle)
      setConversations(prev =>
        prev.map(c => (c.id === id ? { ...c, title: editingTitle } : c))
      )
      setEditingId(null)
      toast.success('タイトルを更新しました')
    } catch (error) {
      toast.error('更新に失敗しました')
    }
  }

  const startEditing = (id: string, currentTitle: string) => {
    setEditingId(id)
    setEditingTitle(currentTitle)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return '今日'
    if (days === 1) return '昨日'
    if (days < 7) return `${days}日前`
    if (days < 30) return `${Math.floor(days / 7)}週間前`
    return date.toLocaleDateString('ja-JP')
  }

  if (!isAuthenticated) return null

  const sidebarContent = (
    <>
      <div className="p-4 border-b border-gray-200 bg-white">
        <button
          onClick={() => {
            onNewConversation()
            setIsMobileOpen(false)
          }}
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors"
        >
          <FaPlus />
          <span>新しい会話</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto bg-white">
        {isLoading ? (
          <div className="p-4 text-gray-500 text-center">読み込み中...</div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-gray-500 text-center">
            <FaComments className="mx-auto mb-2 text-3xl text-gray-400" />
            <p>会話履歴がありません</p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map(conversation => (
              <div
                key={conversation.id}
                className={clsx(
                  'group rounded-md transition-colors border border-transparent hover:bg-gray-100',
                  selectedConversationId === conversation.id && 'bg-indigo-50 border-indigo-200'
                )}
              >
                {editingId === conversation.id ? (
                  <div className="p-2 flex items-center space-x-2">
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={e => setEditingTitle(e.target.value)}
                      onBlur={() => handleEditTitle(conversation.id)}
                      onKeyDown={e => {
                        if (e.key === 'Enter') handleEditTitle(conversation.id)
                        if (e.key === 'Escape') setEditingId(null)
                      }}
                      className="flex-1 px-2 py-1 bg-white border border-gray-300 text-gray-800 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      autoFocus
                    />
                  </div>
                ) : (
                  <div
                    className="p-2 flex items-center justify-between cursor-pointer"
                    onClick={() => {
                      onSelectConversation(conversation.id)
                      setIsMobileOpen(false)
                    }}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-gray-800 text-sm truncate">{conversation.title}</p>
                      <p className="text-gray-500 text-xs">
                        {formatDate(conversation.updated_at)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          startEditing(conversation.id, conversation.title)
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <FaEdit size={14} />
                      </button>
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          handleDeleteConversation(conversation.id)
                        }}
                        className="p-1 text-gray-400 hover:text-red-500"
                      >
                        <FaTrash size={14} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="md:hidden fixed top-20 left-4 z-40 p-2 bg-white text-gray-700 border border-gray-200 rounded-md shadow-sm"
      >
        <FaBars size={20} />
      </button>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed md:relative w-72 h-full bg-white flex flex-col z-50 transition-transform duration-300 border-r border-gray-200',
          'md:translate-x-0',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Mobile close button */}
        <button
          onClick={() => setIsMobileOpen(false)}
          className="md:hidden absolute top-4 right-4 text-gray-400 hover:text-white"
        >
          <FaTimes size={20} />
        </button>

        {sidebarContent}
      </div>
    </>
  )
}

export default ConversationSidebar
