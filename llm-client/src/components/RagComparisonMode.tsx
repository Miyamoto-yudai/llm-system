import React, { useState } from 'react'
import { FaPaperPlane, FaTrash, FaDownload, FaArrowLeft } from 'react-icons/fa'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import ComparisonChat from './ComparisonChat'
import QuickTemplates from './QuickTemplates'
import { useRagComparisonSocket } from '../hooks/useRagComparisonSocket'
import toast from 'react-hot-toast'

const RagComparisonMode: React.FC = () => {
  const {
    messagesWithRag,
    messagesWithoutRag,
    chunkWithRag,
    chunkWithoutRag,
    inputText,
    setInputText,
    onSubmit,
    resetChat,
    isConnected,
    isProcessing,
    responseType
  } = useRagComparisonSocket()

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
        with_rag: messagesWithRag,
        without_rag: messagesWithoutRag
      },
      statistics: {
        with_rag: {
          total_messages: messagesWithRag.length,
          clarifying_questions: messagesWithRag.filter(m =>
            m.speakerId === 0 && m.text.includes('【確認ステップ')
          ).length,
          rag_indicators: messagesWithRag.filter(m =>
            m.speakerId === 0 && (m.text.includes('【罪名予測（RAG）】') || m.text.includes('【量刑予測（RAG）】'))
          ).length
        },
        without_rag: {
          total_messages: messagesWithoutRag.length,
          clarifying_questions: messagesWithoutRag.filter(m =>
            m.speakerId === 0 && m.text.includes('【確認ステップ')
          ).length
        }
      },
      response_type: responseType
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rag-comparison-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('RAG比較結果をエクスポートしました')
  }

  const handleTemplateSelect = (template: string) => {
    setInputText(template)
  }

  // 応答タイプの日本語表示
  const getResponseTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'predict_crime_type': '罪名予測',
      'predict_punishment': '量刑予測',
      'predict_crime_and_punishment': '罪名・量刑統合予測',
      'legal_process': '法プロセス'
    }
    return labels[type] || type
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
              <h1 className="text-xl font-bold text-gray-800">RAG比較検証モード</h1>
              <p className="text-sm text-gray-600">
                RAGあり/なしの予測精度を比較
                {!isConnected && (
                  <span className="ml-2 text-red-600">(未接続)</span>
                )}
                {responseType && (
                  <span className="ml-2 text-blue-600">
                    （{getResponseTypeLabel(responseType)}）
                  </span>
                )}
                <span className="mx-2">|</span>
                <Link
                  to="/comparison"
                  className="text-blue-600 hover:underline"
                >
                  データあり/なし比較モードに切り替え
                </Link>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              disabled={messagesWithRag.length === 0}
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
            title="RAGあり（判例参照）"
            messages={messagesWithRag}
            chunks={chunkWithRag}
            isProcessing={isProcessing}
            variant="with-rag"
            subtitle=""
          />
          <ComparisonChat
            title="RAGなし（通常モード）"
            messages={messagesWithoutRag}
            chunks={chunkWithoutRag}
            isProcessing={isProcessing}
            variant="without-rag"
            subtitle=""
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
              placeholder="両方のモード（RAGあり/なし）で同じ質問を送信します..."
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
              <div className="text-gray-600 mb-1">RAGあり:</div>
              <div className="space-y-1">
                <div>
                  <span className="text-gray-500">深掘り質問: </span>
                  <span className="font-medium">
                    {messagesWithRag.filter(m =>
                      m.speakerId === 0 && m.text.includes('【確認ステップ')
                    ).length}回
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">RAG使用回数: </span>
                  <span className="font-medium">
                    {messagesWithRag.filter(m =>
                      m.speakerId === 0 && (m.text.includes('【罪名予測（RAG）】') || m.text.includes('【量刑予測（RAG）】'))
                    ).length}回
                  </span>
                </div>
              </div>
            </div>
            <div>
              <div className="text-gray-600 mb-1">RAGなし:</div>
              <div className="space-y-1">
                <div>
                  <span className="text-gray-500">深掘り質問: </span>
                  <span className="font-medium">
                    {messagesWithoutRag.filter(m =>
                      m.speakerId === 0 && m.text.includes('【確認ステップ')
                    ).length}回
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
          <strong>注意:</strong> RAG機能を使用するには、サーバー側で<code className="bg-blue-100 px-1 py-0.5 rounded">ENABLE_RAG=true</code>と<code className="bg-blue-100 px-1 py-0.5 rounded">VECTOR_STORE_ID</code>の設定が必要です。
        </div>
      </div>
    </div>
  )
}

export default RagComparisonMode
