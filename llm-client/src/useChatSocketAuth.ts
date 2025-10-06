import { useCallback, useEffect, useRef, useState } from 'react'
import { Message } from './components/Dialog'
import { storage } from './utils/storage'
import { getWebSocketUrl } from './services/api.config'

export const useChatSocketAuth = (conversationId: string | null, selectedGenre: string | null = null) => {
  const introText = "こんにちは、法律相談LawFlowです。刑事事件の法律相談に無料で回答します。以下の注意事項をお読みいただいた上で、ご相談ください。\n＊注意事項＊\n○本サービスによる回答がユーザー様のご希望に沿ったり有益であることやいかなる誤りもないことは保証できません。\n○本サービスの利用に起因してユーザー様に生じたあらゆる損害について一切の責任を負いません。\n○投稿した発言は削除できません\n○正確に回答できない可能性がありますので、弁護士に相談するなどして、回答の正確性を確保するようにしてください。"
  const welcomeText = "こんにちは。ご相談やご質問があればお気軽にお知らせください。"

  const [inputText, setInputText] = useState<string>('')
  const [chunk, setChunk] = useState<string[]>([])
  const [messages, setMessages] = useState<Message[]>([
    { speakerId: 0, text: introText },
    { speakerId: 0, text: welcomeText }
  ])
  const [isConnected, setIsConnected] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(conversationId)

  const socketRef = useRef<WebSocket>()
  const chunkAccumulator = useRef<string>('')
  const hasWelcomeRef = useRef<boolean>(true)
  const genreRef = useRef<string | null>(selectedGenre)

  // Update genre ref when it changes
  useEffect(() => {
    genreRef.current = selectedGenre
  }, [selectedGenre])

  const connectWebSocket = useCallback(() => {
    const token = storage.getToken()

    if (token) {
      // Authenticated WebSocket
      const params: Record<string, string> = { token }
      if (conversationId) {
        params.conversation_id = conversationId
      }
      const url = getWebSocketUrl('/ws/chat', params)
      socketRef.current = new WebSocket(url)
    } else {
      // Guest WebSocket
      const url = getWebSocketUrl('/chat')
      socketRef.current = new WebSocket(url)
    }

    const ws = socketRef.current

    ws.onopen = () => {
      setIsConnected(true)
      // Request history if continuing a conversation
      if (conversationId && token) {
        ws.send(JSON.stringify({ type: 'history_request' }))
      }
    }

    ws.onmessage = (event: MessageEvent<string>) => {
      const data = JSON.parse(event.data)

      // Handle different message types
      if (data.type === 'conversation_id') {
        setCurrentConversationId(data.conversation_id)
        // Notify parent component about the new conversation ID
        if (window.dispatchEvent) {
          window.dispatchEvent(new CustomEvent('conversationCreated', {
            detail: { conversationId: data.conversation_id }
          }))
        }
      } else if (data.type === 'history') {
        // Load conversation history
        const historyMessages: Message[] = [
          { speakerId: 0, text: introText },
          { speakerId: 0, text: welcomeText }
        ]
        hasWelcomeRef.current = true
        data.messages.forEach((msg: any) => {
          if (msg.content === welcomeText && hasWelcomeRef.current) {
            return
          }
          historyMessages.push({
            speakerId: msg.role === 'user' ? 1 : 0,
            text: msg.content
          })
          if (msg.content === welcomeText) {
            hasWelcomeRef.current = true
          }
        })
        setMessages(historyMessages)
      } else if (data.text) {
        // Handle chat response
        const text = data.text
        if (text === '<start>') {
          chunkAccumulator.current = ''
        } else if (text === '<end>') {
          const message = chunkAccumulator.current
          if (message === welcomeText && hasWelcomeRef.current) {
            setChunk([])
            chunkAccumulator.current = ''
            return
          }
          addMessage(0, message)
          if (message === welcomeText) {
            hasWelcomeRef.current = true
          }
          setChunk([])
          chunkAccumulator.current = ''
        } else {
          addChunk(text)
          chunkAccumulator.current += text
        }
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }

    ws.onclose = () => {
      setIsConnected(false)
    }

    return ws
  }, [conversationId])

  const addMessage = useCallback((speakerId: number, text: string) => {
    setMessages(ms => [...ms, { speakerId, text }])
  }, [])

  const addChunk = useCallback((text: string) => {
    setChunk(chks => [...chks, text])
  }, [])

  useEffect(() => {
    const ws = connectWebSocket()

    return () => {
      ws.close()
    }
  }, [conversationId])

  const onSubmit = useCallback(async () => {
    if (!inputText.trim() || !socketRef.current || !isConnected) return

    // Add user message to UI
    setMessages(ms => [...ms, { speakerId: 1, text: inputText }])

    // Prepare messages array
    const arr = messages.concat([{ speakerId: 1, text: inputText }]).slice(1)

    // Send to WebSocket
    const token = storage.getToken()
    if (token) {
      // For authenticated users, send in the new format with genre
      const payload: any = { messages: arr }
      if (genreRef.current) {
        payload.genre = genreRef.current
        console.log("genre> ", genreRef.current)
      }
      socketRef.current.send(JSON.stringify(payload))
    } else {
      // For guests, use the old format with genre
      const payload: any = { messages: arr }
      if (genreRef.current) {
        payload.genre = genreRef.current
        console.log("genre> ", genreRef.current)
      }
      socketRef.current.send(JSON.stringify(payload))
    }

    setInputText('')
  }, [inputText, messages, isConnected])

  const resetChat = useCallback(() => {
    setMessages([
      { speakerId: 0, text: introText },
      { speakerId: 0, text: welcomeText }
    ])
    setChunk([])
    setInputText('')
    chunkAccumulator.current = ''
    hasWelcomeRef.current = true
  }, [])

  return {
    inputText,
    setInputText,
    messages,
    onSubmit,
    chunk,
    isConnected,
    currentConversationId,
    resetChat
  }
}
