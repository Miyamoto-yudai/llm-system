import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    sync_client: Optional[MongoClient] = None
    database = None
    sync_database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection for async operations"""
    mongodb.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    )
    mongodb.database = mongodb.client[
        os.getenv("MONGODB_DATABASE", "llm_legal_system")
    ]
    print("Connected to MongoDB (async)")

def connect_to_mongo_sync():
    """Create database connection for sync operations"""
    mongodb.sync_client = MongoClient(
        os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    )
    mongodb.sync_database = mongodb.sync_client[
        os.getenv("MONGODB_DATABASE", "llm_legal_system")
    ]
    print("Connected to MongoDB (sync)")

async def close_mongo_connection():
    """Close database connection for async operations"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB (async)")

def close_mongo_connection_sync():
    """Close database connection for sync operations"""
    if mongodb.sync_client:
        mongodb.sync_client.close()
        print("Disconnected from MongoDB (sync)")

def get_database():
    """Get async database instance"""
    return mongodb.database

def get_sync_database():
    """Get sync database instance"""
    return mongodb.sync_database

async def init_indexes():
    """Initialize database indexes"""
    db = get_database()

    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)

    # Sessions collection indexes
    await db.sessions.create_index("user_id")
    await db.sessions.create_index("token", unique=True)
    await db.sessions.create_index("expires_at")

    # Conversations collection indexes
    await db.conversations.create_index("user_id")
    await db.conversations.create_index("created_at")

    # Messages collection indexes
    await db.messages.create_index("conversation_id")
    await db.messages.create_index("created_at")

    print("Database indexes created")