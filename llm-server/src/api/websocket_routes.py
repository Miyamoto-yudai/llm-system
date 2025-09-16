import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, Query
from src.database.connection import get_database
from src.database.models import MessageModel, ConversationModel
from src.auth.authentication import decode_token
from datetime import datetime
import src.chat as c


async def handle_authenticated_chat(ws: WebSocket, token: str, conversation_id: Optional[str] = None):
    """Handle WebSocket chat for authenticated users"""
    await ws.accept()

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

    # Create new conversation or use existing one
    if not conversation_id:
        conv_model = ConversationModel(
            user_id=user_id,
            title="新しい会話"
        )
        result = await db.conversations.insert_one(conv_model.dict(by_alias=True))
        conversation_id = str(result.inserted_id)
        conv_obj_id = result.inserted_id
    else:
        # Verify conversation belongs to user
        conversation = await db.conversations.find_one({
            "_id": conversation_id,
            "user_id": user_id
        })
        if not conversation:
            await ws.send_json({"error": "Conversation not found"})
            await ws.close()
            return
        conv_obj_id = conversation["_id"]

    # Send conversation ID to client
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

    while True:
        try:
            json_string = await ws.receive_text()
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
            print("HIST ", hist)

            acc = []
            for h in hist:
                if h["speakerId"] == 1:
                    acc.append({"role": "user", "content": h['text']})
                else:
                    acc.append({"role": "assistant", "content": h['text']})

            # Save user message
            if acc and acc[-1]["role"] == "user":
                user_msg = MessageModel(
                    conversation_id=conversation_id,
                    role="user",
                    content=acc[-1]["content"]
                )
                await db.messages.insert_one(user_msg.dict(by_alias=True))

            # Generate response
            rep = c.reply(acc)
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

            # Save assistant message
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

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user_id}")
            break
        except Exception as e:
            print(f"Error in WebSocket: {e}")
            logging.error(e)
            await ws.send_json({"error": "An error occurred"})
            break