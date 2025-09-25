import React, { useState } from 'react'
import { FaPaperPlane, FaTrash, FaDownload, FaArrowLeft } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import ComparisonChat from './ComparisonChat'
import QuickTemplates from './QuickTemplates'
import { useComparisonSocket } from '../hooks/useComparisonSocket'
import toast from 'react-hot-toast'

const ComparisonMode: React.FC = () => {
  const {
    messagesWithData,
    messagesWithoutData,
    chunkWithData,
    chunkWithoutData,
    inputText,
    setInputText,
    onSubmit,
    resetChat,
    isConnected,
    isProcessing
  } = useComparisonSocket()

  const [isComposing, setIsComposing] = useState(false)

  const handleSubmit = () => {
    if (inputText.trim() && !isProcessing) {
      onSubmit()
    }
  }

  const handleClearChat = () => {
    resetChat()
    toast.success('会話をクリアしました')
  }

  const handleExport = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      comparison: {
        with_data: messagesWithData,
        without_data: messagesWithoutData
      },
      statistics: {
        with_data: {
          total_messages: messagesWithData.length,
          clarifying_questions: messagesWithData.filter(m =>
            m.speakerId === 0 && m.text.includes('【確認ステップ')
          ).length
        },
        without_data: {
          total_messages: messagesWithoutData.length,
          clarifying_questions: messagesWithoutData.filter(m =>
            m.speakerId === 0 && m.text.includes('【確認ステップ')
          ).length
        }
      }
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `comparison-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('比較結果をエクスポートしました')
  }

  const handleTemplateSelect = (template: string) => {
    setInputText(template)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <FaArrowLeft />
              <span>通常モードに戻る</span>
            </Link>
            <div className="border-l border-gray-300 h-6 mx-2" />
            <div>
              <h1 className="text-xl font-bold text-gray-800">比較検証モード</h1>
              <p className="text-sm text-gray-600">
                深掘り質問の出力傾向を比較
                {!isConnected && (
                  <span className="ml-2 text-red-600">(未接続)</span>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              disabled={messagesWithData.length === 0}
            >
              <FaDownload className="w-4 h-4" />
              <span>エクスポート</span>
            </button>
            <button
              onClick={handleClearChat}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              <FaTrash className="w-4 h-4" />
              <span>クリア</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
        {/* Chat panels */}
        <div className="flex-1 grid grid-cols-2 gap-4 overflow-hidden">
          <ComparisonChat
            title="データあり（現状方式）"
            messages={messagesWithData}
            chunks={chunkWithData}
            isProcessing={isProcessing}
            variant="with-data"
          />
          <ComparisonChat
            title="LLMのみ"
            messages={messagesWithoutData}
            chunks={chunkWithoutData}
            isProcessing={isProcessing}
            variant="without-data"
          />
        </div>

        {/* Input area */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          {/* Quick templates */}
          <div className="mb-3">
            <QuickTemplates onSelectTemplate={handleTemplateSelect} />
          </div>

          {/* Input field */}
          <div className="flex gap-3">
            <textarea
              className={clsx(
                'flex-1 resize-none outline-none text-gray-800 placeholder-gray-400',
                'min-h-[60px] max-h-[120px] p-3 border rounded-lg',
                isComposing ? 'border-yellow-400 bg-yellow-50/30' : 'border-gray-200'
              )}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onCompositionStart={() => setIsComposing(true)}
              onCompositionEnd={() => setIsComposing(false)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
                  e.preventDefault()
                  handleSubmit()
                }
              }}
              placeholder="両方のモードで同じ質問を送信します..."
              disabled={!isConnected || isProcessing}
              rows={2}
            />
            <button
              onClick={handleSubmit}
              disabled={!inputText.trim() || !isConnected || isProcessing}
              className={clsx(
                'self-end px-6 py-3 rounded-lg font-medium transition-colors',
                'flex items-center gap-2',
                inputText.trim() && isConnected && !isProcessing
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              )}
            >
              <FaPaperPlane className="w-4 h-4" />
              <span>{isProcessing ? '処理中...' : '送信'}</span>
            </button>
          </div>

          {/* Keyboard shortcuts */}
          <div className="mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-3 text-xs text-gray-500">
            <span>Enter: 送信 {isComposing && '(変換中)'}</span>
            <span>Shift+Enter: 改行</span>
            <span className="ml-auto">
              {isProcessing && '両方のモードで処理中...'}
            </span>
          </div>
        </div>

        {/* Comparison statistics */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-800 mb-2">比較統計</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">データあり: </span>
              <span className="font-medium">
                深掘り質問 {
                  messagesWithData.filter(m =>
                    m.speakerId === 0 && m.text.includes('【確認ステップ')
                  ).length
                }回
              </span>
            </div>
            <div>
              <span className="text-gray-600">LLMのみ: </span>
              <span className="font-medium">
                深掘り質問 {
                  messagesWithoutData.filter(m =>
                    m.speakerId === 0 && m.text.includes('【確認ステップ')
                  ).length
                }回
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ComparisonMode