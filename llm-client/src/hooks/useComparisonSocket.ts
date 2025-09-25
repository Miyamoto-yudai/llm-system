import { useState, useEffect, useRef, useCallback } from 'react'
import { getWebSocketUrl } from '../services/api.config'

interface Message {
  speakerId: number
  text: string
  timestamp?: number
}

interface ComparisonResponse {
  with_data?: string
  without_data?: string
}

export const useComparisonSocket = () => {
  const [messagesWithData, setMessagesWithData] = useState<Message[]>([])
  const [messagesWithoutData, setMessagesWithoutData] = useState<Message[]>([])
  const [chunkWithData, setChunkWithData] = useState<string[]>([])
  const [chunkWithoutData, setChunkWithoutData] = useState<string[]>([])
  const [inputText, setInputText] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const messageHistoryRef = useRef<Message[]>([])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = getWebSocketUrl('/ws/comparison')
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('Comparison WebSocket connected')
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
        case 'welcome':
          // Add welcome message to both sides
          if (data.with_data) {
            setMessagesWithData(prev => [...prev, {
              speakerId: 0,
              text: data.with_data,
              timestamp: Date.now()
            }])
          }
          if (data.without_data) {
            setMessagesWithoutData(prev => [...prev, {
              speakerId: 0,
              text: data.without_data,
              timestamp: Date.now()
            }])
          }
          break

        case 'start':
          setChunkWithData([])
          setChunkWithoutData([])
          setIsProcessing(true)
          break

        case 'chunk':
          if (data.with_data) {
            setChunkWithData(prev => [...prev, data.with_data])
          }
          if (data.without_data) {
            setChunkWithoutData(prev => [...prev, data.without_data])
          }
          break

        case 'end':
          // Add complete responses to message history
          if (data.with_data) {
            setMessagesWithData(prev => [...prev, {
              speakerId: 0,
              text: data.with_data,
              timestamp: Date.now()
            }])
          }
          if (data.without_data) {
            setMessagesWithoutData(prev => [...prev, {
              speakerId: 0,
              text: data.without_data,
              timestamp: Date.now()
            }])
          }
          setChunkWithData([])
          setChunkWithoutData([])
          setIsProcessing(false)
          break

        case 'error':
          console.error('Comparison error:', data.message)
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

    setMessagesWithData(prev => [...prev, userMessage])
    setMessagesWithoutData(prev => [...prev, userMessage])

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
    setMessagesWithData([])
    setMessagesWithoutData([])
    setChunkWithData([])
    setChunkWithoutData([])
    messageHistoryRef.current = []
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
    // Use the with_data messages as the reference (they should be the same for user messages)
    messageHistoryRef.current = messagesWithData
  }, [messagesWithData])

  return {
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
  }
}