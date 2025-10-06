import os, sys
import logging
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

import src.gen.lawflow.lc as lc
import src.gen.util as u
import src.chat as c
import src.config as config
from src.database.connection import (
    connect_to_mongo, close_mongo_connection, init_indexes, get_database
)
from src.database.models import MessageModel, ConversationModel
from src.api import session_routes, conversation_routes, websocket_routes, oauth_routes
from src.auth.authentication import decode_token
from datetime import datetime

def log_chat(last_exchange):
    log_file = 'log.txt'
    with open(log_file, 'a', encoding='utf-8') as f:
        for entry in last_exchange:
            f.write(f"{entry['role']}: {entry['content']}\n")
        f.write("\n" + "="*50 + "\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await init_indexes()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
chat_docs1 = u.load("dataset/criminal264.pickle")
chat_docs2 = u.load("dataset/criminalprocedure.pickle")
chat_docs = dict()
chat_docs.update(chat_docs1)
chat_docs.update(chat_docs2)

origins = ["http://localhost:5173","http://notebook.lawflow.jp:5173","http://notebook.lawflow.jp:8000","http://notebook.lawflow.jp:80"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str = Field(title="Request message to LLM.", max_length=1000)

class LLMResponse(BaseModel):
    text: str

@app.get("/healthcheck")
def healthcheck():
    return {}

# Include routers for authentication and conversations
app.include_router(session_routes.router)
app.include_router(oauth_routes.router)
app.include_router(conversation_routes.router)

# 比較モードが有効な場合のみ比較用ルートを追加
if config.COMPARISON_MODE_ENABLED:
    from src.api import comparison_routes
    app.include_router(comparison_routes.router)
    print("Comparison mode routes enabled")

@app.websocket("/chat")
async def websocket_endpoint(ws: WebSocket, token: Optional[str] = Query(None)):
    await ws.accept()

    # Optional: Authenticate user if token is provided
    user_id = None
    conversation_id = None

    # メッセージ処理用のロックを作成
    processing_lock = asyncio.Lock()
    is_processing = False

    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")
            # Create or get conversation for authenticated user
            if user_id:
                db = get_database()
                # Create new conversation
                conv_model = ConversationModel(
                    user_id=user_id,
                    title="新しい会話"
                )
                result = await db.conversations.insert_one(conv_model.dict(by_alias=True))
                conversation_id = str(result.inserted_id)

    while True:
        try:
            json_string = await ws.receive_text()

            # 処理中の場合は新しいメッセージを無視
            async with processing_lock:
                if is_processing:
                    await ws.send_json({'text': '現在処理中です。少々お待ちください。', 'type': 'warning'})
                    continue
                is_processing = True

            try:
                data = json.loads(json_string)
                print("DATA ", data)

                # Support both old format (array) and new format (object with messages and genre)
                if isinstance(data, list):
                    # Old format: direct array of messages
                    hist = data
                    genre = None
                else:
                    # New format: object with messages and optional genre
                    hist = data.get("messages", [])
                    genre = data.get("genre", None)

                print("HIST ", hist)
                print("GENRE ", genre)

                acc = []
                for h in hist:
                    if h["speakerId"] == 1:
                        acc.append({"role": "user", "content": h['text']})
                    else:
                        acc.append({"role": "assistant", "content": h['text']})
                        print("acc:", acc)

                # Save user message if authenticated
                if conversation_id and acc and acc[-1]["role"] == "user":
                    db = get_database()
                    user_msg = MessageModel(
                        conversation_id=conversation_id,
                        role="user",
                        content=acc[-1]["content"]
                    )
                    await db.messages.insert_one(user_msg.dict(by_alias=True))

                rep = c.reply(acc, genre=genre)
                response_text = ""

                await ws.send_json({'text': '<start>'})

                # repがジェネレータの場合とそうでない場合を区別
                if isinstance(rep, str):
                    response_text += rep
                    await ws.send_json({'text': rep})
                else:
                    for x in rep:
                        response_text += x
                        await ws.send_json({'text': x})

                await ws.send_json({'text': '<end>'})

                # Save assistant message if authenticated
                if conversation_id:
                    db = get_database()
                    assistant_msg = MessageModel(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_text
                    )
                    await db.messages.insert_one(assistant_msg.dict(by_alias=True))

                    # Update conversation's updated_at
                    await db.conversations.update_one(
                        {"_id": conv_model.id},
                        {"$set": {"updated_at": datetime.utcnow()}}
                    )

                acc.append({"role": "assistant", "content": response_text})
                log_chat(acc[-2:])

            finally:
                # 処理完了フラグをリセット
                async with processing_lock:
                    is_processing = False

        except WebSocketDisconnect:
            break
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error details: {error_details}")
            logging.error(f"Error details: {error_details}")

            # エラーが発生した場合もフラグをリセット
            async with processing_lock:
                is_processing = False

            resp = LLMResponse(text="申し訳ございません。エラーが発生しました。もう一度お試しください。")
            await ws.send_json(resp.dict())

@app.websocket("/ws/chat")
async def authenticated_websocket_endpoint(
    ws: WebSocket,
    token: str = Query(...),
    conversation_id: Optional[str] = Query(None)
):
    """Authenticated WebSocket endpoint for chat"""
    await websocket_routes.handle_authenticated_chat(ws, token, conversation_id)

