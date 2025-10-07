import { useState, useEffect, useRef, useCallback } from 'react'
import { getWebSocketUrl } from '../services/api.config'

interface Message {
  speakerId: number
  text: string
  timestamp?: number
}

export const useRagComparisonSocket = () => {
  const [messagesWithRag, setMessagesWithRag] = useState<Message[]>([])
  const [messagesWithoutRag, setMessagesWithoutRag] = useState<Message[]>([])
  const [chunkWithRag, setChunkWithRag] = useState<string[]>([])
  const [chunkWithoutRag, setChunkWithoutRag] = useState<string[]>([])
  const [inputText, setInputText] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [responseType, setResponseType] = useState<string>('')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const messageHistoryRef = useRef<Message[]>([])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = getWebSocketUrl('/ws/comparison/rag')
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('RAG Comparison WebSocket connected')
      setIsConnected(true)

      // Send ping every 30 seconds to keep connection alive
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }))
        }
      }, 30000)

      // Store interval ID for cleanup
      (ws as any).pingInterval = pingInterval
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'system':
          console.log('System message:', data.message)
          break

        case 'welcome':
          // Add welcome message to both sides
          if (data.with_rag) {
            setMessagesWithRag(prev => [...prev, {
              speakerId: 0,
              text: data.with_rag,
              timestamp: Date.now()
            }])
          }
          if (data.without_rag) {
            setMessagesWithoutRag(prev => [...prev, {
              speakerId: 0,
              text: data.without_rag,
              timestamp: Date.now()
            }])
          }
          break

        case 'start':
          setChunkWithRag([])
          setChunkWithoutRag([])
          setIsProcessing(true)
          if (data.response_type) {
            setResponseType(data.response_type)
          }
          break

        case 'chunk':
          if (data.with_rag) {
            setChunkWithRag(prev => [...prev, data.with_rag])
          }
          if (data.without_rag) {
            setChunkWithoutRag(prev => [...prev, data.without_rag])
          }
          break

        case 'end':
          // Add complete responses to message history
          if (data.with_rag) {
            setMessagesWithRag(prev => [...prev, {
              speakerId: 0,
              text: data.with_rag,
              timestamp: Date.now()
            }])
          }
          if (data.without_rag) {
            setMessagesWithoutRag(prev => [...prev, {
              speakerId: 0,
              text: data.without_rag,
              timestamp: Date.now()
            }])
          }
          setChunkWithRag([])
          setChunkWithoutRag([])
          setIsProcessing(false)
          break

        case 'error':
          console.error('RAG Comparison error:', data.message)
          // Show error message to user
          const errorMessage = {
            speakerId: 0,
            text: `エラー: ${data.message}`,
            timestamp: Date.now()
          }
          setMessagesWithRag(prev => [...prev, errorMessage])
          setMessagesWithoutRag(prev => [...prev, errorMessage])
          setIsProcessing(false)
          break

        case 'pong':
          // Ignore pong responses
          break

        default:
          console.log('Unknown message type:', data.type)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)

      // Clear ping interval
      if ((ws as any).pingInterval) {
        clearInterval((ws as any).pingInterval)
      }

      // Attempt to reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, 3000)
    }
  }, [])

  // Send message
  const onSubmit = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    if (!inputText.trim() || isProcessing) return

    // Add user message to both sides
    const userMessage: Message = {
      speakerId: 1,
      text: inputText,
      timestamp: Date.now()
    }

    setMessagesWithRag(prev => [...prev, userMessage])
    setMessagesWithoutRag(prev => [...prev, userMessage])

    // Create combined message history for sending
    const combinedHistory = [...messageHistoryRef.current, userMessage]
    messageHistoryRef.current = combinedHistory

    // Send to WebSocket
    wsRef.current.send(JSON.stringify({
      messages: combinedHistory
    }))

    setInputText('')
  }, [inputText, isProcessing])

  // Reset chat
  const resetChat = useCallback(() => {
    setMessagesWithRag([])
    setMessagesWithoutRag([])
    setChunkWithRag([])
    setChunkWithoutRag([])
    messageHistoryRef.current = []
    setResponseType('')
  }, [])

  // Initialize connection
  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        const ws = wsRef.current
        if ((ws as any).pingInterval) {
          clearInterval((ws as any).pingInterval)
        }
        ws.close()
      }
    }
  }, [connect])

  // Update message history reference
  useEffect(() => {
    // Use the with_rag messages as the reference (they should be the same for user messages)
    messageHistoryRef.current = messagesWithRag
  }, [messagesWithRag])

  return {
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
  }
}
