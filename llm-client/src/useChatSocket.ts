import { useCallback, useEffect, useRef, useState } from 'react'

import { Message } from './components/Dialog'

export const useChatSocket = (selectedGenre: string | null = null) => {
  const introText = "こんにちは、法律相談LawFlowです。刑事事件の法律相談に無料で回答します。以下の注意事項をお読みいただいた上で、ご相談ください。\n＊注意事項＊\n○本サービスによる回答がユーザー様のご希望に沿ったり有益であることやいかなる誤りもないことは保証できません。\n○本サービスの利用に起因してユーザー様に生じたあらゆる損害について一切の責任を負いません。\n○投稿した発言は削除できません\n○正確に回答できない可能性がありますので、弁護士に相談するなどして、回答の正確性を確保するようにしてください。"
  const welcomeText = "こんにちは。ご相談やご質問があればお気軽にお知らせください。"
  const [inputText, setInputText] = useState<string>('')
  const [chunk, setChunk] = useState<string[]>([])
  var chk = ""
  const [messages, setMessages] = useState<Message[]>([
    { speakerId: 0, text: introText },
    { speakerId: 0, text: welcomeText }
  ])
  const genreRef = useRef<string | null>(selectedGenre)

  // Update genre ref when it changes
  useEffect(() => {
    genreRef.current = selectedGenre
  }, [selectedGenre])
  
  const addMessage = useCallback(
    (speakerId: number, text: string) => {
      setMessages((ms) => [...ms, { speakerId: speakerId, text: text }])
    },
    [setMessages]
  )
  const addChunk = useCallback(
    (text: string) => {
      setChunk((chks) => {
	//console.log(text)
	//console.log([...chks, text])
	//console.log(chunk)
	return [...chks, text]
	})
    },
    [setChunk]
  )

  const socketRef = useRef<WebSocket>()
  const hasWelcomeRef = useRef<boolean>(true)
  useEffect(() => {
    //const websocket = new WebSocket('wss://llm-server.lawflow.jp/chat') // 本番用
    //const websocket = new WebSocket('ws://notebook.lawflow.jp:8080/chat') // 開発用
    const websocket = new WebSocket('ws://localhost:8080/chat')//ローカルサーバのテスト用
    socketRef.current = websocket

    const onMessage = (event: MessageEvent<string>) => {
      const text = JSON.parse(event.data).text ?? ''
      console.log("received text> ", text)
      if(text=="<start>"){
	//none
      }else if(text=="<end>"){
	const message = chk
	if(message === welcomeText && hasWelcomeRef.current){
	  setChunk([])
	  chk=""
	  return
	}
	addMessage(0, message)
	if(message === welcomeText){
	  hasWelcomeRef.current = true
	}
	setChunk([])
	chk=""
      }else{
	addChunk(text)
	chk=chk+text
      }
    }
    websocket.addEventListener('message', onMessage)

    return () => {
      websocket.close()
      websocket.removeEventListener('message', onMessage)
    }
  }, [])
  const onSubmit = useCallback(async () => {
    console.log("input text> ", inputText)
    setMessages((ms) => [...ms, { speakerId: 1, text: inputText }])
    var arr = messages.concat([{speakerId:1, text: inputText}])
    var arr = arr.slice(1);
    console.log("arr> ", arr)

    // Include genre information if selected
    const payload: any = { messages: arr }
    if (genreRef.current) {
      payload.genre = genreRef.current
      console.log("genre> ", genreRef.current)
    }

    var json_string = JSON.stringify(payload);
    console.log("json> ", json_string)
    socketRef.current?.send(json_string)
    setInputText('')

  }, [addMessage, setInputText, inputText, messages])
  return { inputText, setInputText, messages, onSubmit, chunk, setChunk}
}
