import json
import logging
import asyncio
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, Query
from src.database.connection import get_database
from src.database.models import MessageModel, ConversationModel
from src.auth.authentication import decode_token
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
import src.chat as c
from src.utils.title_generator import generate_conversation_title
from src.config import is_rag_enabled


async def handle_authenticated_chat(ws: WebSocket, token: str, conversation_id: Optional[str] = None):
    """Handle WebSocket chat for authenticated users"""
    await ws.accept()

    # メッセージ処理用のロックを作成
    processing_lock = asyncio.Lock()
    is_processing = False

    # Authenticate user
    payload = decode_token(token)
    if not payload:
        await ws.send_json({"error": "Invalid token"})
        await ws.close()
        return

    user_id = payload.get("sub")
    if not user_id:
        await ws.send_json({"error": "Invalid user"})
        await ws.close()
        return

    db = get_database()

    # Initialize conversation variables
    conv_obj_id = None
    is_new_conversation = False

    # Handle existing conversation
    if conversation_id:
        # Verify conversation belongs to user
        try:
            obj_id = ObjectId(conversation_id)
        except (InvalidId, TypeError):
            await ws.send_json({"error": "Conversation not found"})
            await ws.close()
            return

        conversation = await db.conversations.find_one({
            "_id": obj_id,
            "user_id": user_id
        })
        if not conversation:
            await ws.send_json({"error": "Conversation not found"})
            await ws.close()
            return
        conv_obj_id = conversation["_id"]
    else:
        # Mark as new conversation (will be created on first message)
        is_new_conversation = True

    # Send conversation ID to client (null for new conversations)
    if not is_new_conversation:
        await ws.send_json({"type": "conversation_id", "conversation_id": conversation_id})

    # Load existing messages if continuing a conversation
    existing_messages = []
    if conversation_id:
        messages = await db.messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1).to_list(None)

        for msg in messages:
            existing_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 初回会話開始時に挨拶を送信（新規会話の場合はまだ保存しない）
    if not existing_messages and not is_new_conversation:
        greeting = c.WELCOME_MESSAGE
        await ws.send_json({'text': '<start>'})
        await ws.send_json({'text': greeting})
        await ws.send_json({'text': '<end>'})

        greeting_msg = MessageModel(
            conversation_id=conversation_id,
            role="assistant",
            content=greeting
        )
        await db.messages.insert_one(greeting_msg.dict(by_alias=True))

        await db.conversations.update_one(
            {"_id": conv_obj_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )

        existing_messages.append({"role": "assistant", "content": greeting})
    elif is_new_conversation:
        # 新規会話の場合は挨拶だけ送信（保存はしない）
        greeting = c.WELCOME_MESSAGE
        await ws.send_json({'text': '<start>'})
        await ws.send_json({'text': greeting})
        await ws.send_json({'text': '<end>'})
        existing_messages.append({"role": "assistant", "content": greeting})

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

                # Handle different message types
                if data.get("type") == "history_request":
                    # Send existing messages
                    await ws.send_json({
                        "type": "history",
                        "messages": existing_messages
                    })
                    continue

                # Process chat message
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

                # Create conversation on first user message if needed
                if is_new_conversation and acc and acc[-1]["role"] == "user":
                    user_first_message = acc[-1]["content"]

                    # Generate title based on user's first message
                    title = generate_conversation_title(user_first_message)

                    # Create the conversation
                    conv_model = ConversationModel(
                        user_id=user_id,
                        title=title
                    )
                    result = await db.conversations.insert_one(conv_model.dict(by_alias=True))
                    conversation_id = str(result.inserted_id)
                    conv_obj_id = result.inserted_id
                    is_new_conversation = False

                    # Send conversation ID to client
                    await ws.send_json({"type": "conversation_id", "conversation_id": conversation_id})

                    # Save the welcome message if it exists
                    if existing_messages and existing_messages[0]["content"] == c.WELCOME_MESSAGE:
                        greeting_msg = MessageModel(
                            conversation_id=conversation_id,
                            role="assistant",
                            content=c.WELCOME_MESSAGE
                        )
                        await db.messages.insert_one(greeting_msg.dict(by_alias=True))

                # Save user message (skip if no conversation yet)
                if acc and acc[-1]["role"] == "user" and conversation_id:
                    user_msg = MessageModel(
                        conversation_id=conversation_id,
                        role="user",
                        content=acc[-1]["content"]
                    )
                    await db.messages.insert_one(user_msg.dict(by_alias=True))

                    # Update title if it's still "新しい会話" and this is first user message
                    if conversation_id:
                        conversation = await db.conversations.find_one({"_id": conv_obj_id})
                        if conversation and conversation.get("title") == "新しい会話":
                            # Check if this is the first user message
                            message_count = await db.messages.count_documents({
                                "conversation_id": conversation_id,
                                "role": "user"
                            })
                            if message_count == 1:  # Just saved the first user message
                                # Generate and update title
                                new_title = generate_conversation_title(acc[-1]["content"])
                                await db.conversations.update_one(
                                    {"_id": conv_obj_id},
                                    {"$set": {"title": new_title}}
                                )

                # Generate response
                use_rag = is_rag_enabled()
                rep = c.reply(acc, genre=genre, use_rag=use_rag)
                response_text = ""

                await ws.send_json({'text': '<start>'})

                if isinstance(rep, str):
                    response_text += rep
                    await ws.send_json({'text': rep})
                else:
                    for x in rep:
                        response_text += x
                        await ws.send_json({'text': x})

                await ws.send_json({'text': '<end>'})

                # Save assistant message (only if conversation exists)
                if conversation_id:
                    assistant_msg = MessageModel(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_text
                    )
                    await db.messages.insert_one(assistant_msg.dict(by_alias=True))

                    # Update conversation's updated_at
                    await db.conversations.update_one(
                        {"_id": conv_obj_id},
                        {"$set": {"updated_at": datetime.utcnow()}}
                    )

                # Update local history
                existing_messages.append({"role": "user", "content": acc[-1]["content"]})
                existing_messages.append({"role": "assistant", "content": response_text})

            finally:
                # 処理完了フラグをリセット
                async with processing_lock:
                    is_processing = False

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id}")
            break
        except Exception as e:
            print(f"Error in WebSocket: {e}")
            logging.error(e)

            # エラーが発生した場合もフラグをリセット
            async with processing_lock:
                is_processing = False

            await ws.send_json({"error": "申し訳ございません。エラーが発生しました。もう一度お試しください。"})
            break
