import { useCallback, useEffect, useRef, useState } from 'react'

import { Message } from './components/Dialog'

export const useChatSocket = () => {
  const t = "こんにちは、法律相談LawFlowです。刑事事件の法律相談に無料で回答します。以下の注意事項をお読みいただいた上で、ご相談ください。\n＊注意事項＊\n○本サービスによる回答がユーザー様のご希望に沿ったり有益であることやいかなる誤りもないことは保証できません。\n○本サービスの利用に起因してユーザー様に生じたあらゆる損害について一切の責任を負いません。\n○投稿した発言は削除できません\n○正確に回答できない可能性がありますので、弁護士に相談するなどして、回答の正確性を確保するようにしてください。"
  const [inputText, setInputText] = useState<string>('')
  const [chunk, setChunk] = useState<string[]>([])
  var chk = ""
  const [messages, setMessages] = useState<Message[]>([
    { speakerId: 0, text: t},
  ])

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
  useEffect(() => {
    //const websocket = new WebSocket('wss://llm-server.lawflow.jp/chat') // 本番用
    //const websocket = new WebSocket('ws://notebook.lawflow.jp:8080/chat') // 開発用
    const websocket = new WebSocket('ws://127.0.0.1:8080/chat')//ローカルサーバのテスト用
    socketRef.current = websocket

    const onMessage = (event: MessageEvent<string>) => {
      const text = JSON.parse(event.data).text ?? ''
      console.log("received text> ", text)
      if(text=="<start>"){
	//none
      }else if(text=="<end>"){
	addMessage(0, chk)
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
    var json_string = JSON.stringify(arr);
    console.log("json> ", json_string)
    //socketRef.current?.send(inputText)
    socketRef.current?.send(json_string)
    setInputText('')

    

  }, [addMessage, setInputText, inputText, messages])
  return { inputText, setInputText, messages, onSubmit, chunk, setChunk}
}
