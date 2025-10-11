from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.database.connection import get_database
from src.database.models import (
    ConversationCreate, ConversationResponse, ConversationWithMessages,
    MessageCreate, MessageResponse, ConversationModel, MessageModel
)
from src.auth.authentication import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    db = get_database()

    conversations = await db.conversations.find(
        {"user_id": str(current_user["_id"])}
    ).sort("updated_at", -1).skip(skip).limit(limit).to_list(None)

    result = []
    for conv in conversations:
        # Count messages in conversation
        message_count = await db.messages.count_documents(
            {"conversation_id": str(conv["_id"])}
        )

        result.append(ConversationResponse(
            id=str(conv["_id"]),
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            message_count=message_count
        ))

    return result


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    db = get_database()

    conv_model = ConversationModel(
        user_id=str(current_user["_id"]),
        title=conversation.title
    )

    result = await db.conversations.insert_one(conv_model.model_dump(by_alias=True))

    return ConversationResponse(
        id=str(result.inserted_id),
        title=conv_model.title,
        created_at=conv_model.created_at,
        updated_at=conv_model.updated_at,
        message_count=0
    )


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversation with all its messages"""
    db = get_database()

    # Verify conversation belongs to user
    conversation = await db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": str(current_user["_id"])
    })

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages
    messages = await db.messages.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1).to_list(None)

    message_responses = [
        MessageResponse(
            id=str(msg["_id"]),
            role=msg["role"],
            content=msg["content"],
            created_at=msg["created_at"]
        )
        for msg in messages
    ]

    return ConversationWithMessages(
        id=str(conversation["_id"]),
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        messages=message_responses
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a message to a conversation"""
    db = get_database()

    # Verify conversation belongs to user
    conversation = await db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": str(current_user["_id"])
    })

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Create message
    msg_model = MessageModel(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content
    )

    result = await db.messages.insert_one(msg_model.model_dump(by_alias=True))

    # Update conversation's updated_at
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    return MessageResponse(
        id=str(result.inserted_id),
        role=msg_model.role,
        content=msg_model.content,
        created_at=msg_model.created_at
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    db = get_database()

    # Verify conversation belongs to user
    conversation = await db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": str(current_user["_id"])
    })

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete all messages
    await db.messages.delete_many({"conversation_id": conversation_id})

    # Delete conversation
    await db.conversations.delete_one({"_id": ObjectId(conversation_id)})

    return {"message": "Conversation deleted successfully"}


@router.put("/{conversation_id}")
async def update_conversation_title(
    conversation_id: str,
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a conversation's title"""
    db = get_database()

    # Verify conversation belongs to user
    conv = await db.conversations.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": str(current_user["_id"])
    })

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Update title
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$set": {
                "title": conversation.title,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Conversation title updated successfully"}