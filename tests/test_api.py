import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_server.main import app
from src.database.connection import get_database, mongodb

# Test client
client = TestClient(app)

# Test data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

class TestAuthentication:
    """認証関連のテスト"""

    def test_register_user(self):
        """ユーザー登録のテスト"""
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user["email"]
        assert data["user"]["username"] == test_user["username"]
        return data["access_token"]

    def test_login_user(self):
        """ログインのテスト"""
        # First register
        client.post("/api/auth/register", json=test_user)

        # Then login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user["email"]
        return data["access_token"]

    def test_get_current_user(self):
        """現在のユーザー情報取得のテスト"""
        # Register and get token
        response = client.post("/api/auth/register", json=test_user)
        token = response.json()["access_token"]

        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]

    def test_invalid_login(self):
        """無効なログインのテスト"""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401


class TestConversations:
    """会話管理関連のテスト"""

    def get_auth_headers(self):
        """認証ヘッダーを取得"""
        response = client.post("/api/auth/register", json={
            "username": "convtest",
            "email": "conv@example.com",
            "password": "testpassword123"
        })
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_conversation(self):
        """会話作成のテスト"""
        headers = self.get_auth_headers()

        conv_data = {"title": "テスト会話"}
        response = client.post("/api/conversations", json=conv_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "テスト会話"
        assert "id" in data
        return data["id"]

    def test_get_conversations(self):
        """会話一覧取得のテスト"""
        headers = self.get_auth_headers()

        # Create a conversation first
        conv_data = {"title": "テスト会話"}
        client.post("/api/conversations", json=conv_data, headers=headers)

        # Get conversations
        response = client.get("/api/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_add_message_to_conversation(self):
        """会話にメッセージ追加のテスト"""
        headers = self.get_auth_headers()

        # Create conversation
        conv_data = {"title": "テスト会話"}
        conv_response = client.post("/api/conversations", json=conv_data, headers=headers)
        conv_id = conv_response.json()["id"]

        # Add message
        message_data = {
            "role": "user",
            "content": "テストメッセージ"
        }
        response = client.post(
            f"/api/conversations/{conv_id}/messages",
            json=message_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"
        assert data["content"] == "テストメッセージ"

    def test_get_conversation_with_messages(self):
        """メッセージ付き会話詳細取得のテスト"""
        headers = self.get_auth_headers()

        # Create conversation
        conv_data = {"title": "テスト会話"}
        conv_response = client.post("/api/conversations", json=conv_data, headers=headers)
        conv_id = conv_response.json()["id"]

        # Add messages
        messages = [
            {"role": "user", "content": "質問です"},
            {"role": "assistant", "content": "回答です"}
        ]

        for msg in messages:
            client.post(
                f"/api/conversations/{conv_id}/messages",
                json=msg,
                headers=headers
            )

        # Get conversation with messages
        response = client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "テスト会話"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "質問です"
        assert data["messages"][1]["content"] == "回答です"

    def test_delete_conversation(self):
        """会話削除のテスト"""
        headers = self.get_auth_headers()

        # Create conversation
        conv_data = {"title": "削除テスト会話"}
        conv_response = client.post("/api/conversations", json=conv_data, headers=headers)
        conv_id = conv_response.json()["id"]

        # Delete conversation
        response = client.delete(f"/api/conversations/{conv_id}", headers=headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert response.status_code == 404


def cleanup_test_data():
    """テストデータのクリーンアップ"""
    if mongodb.sync_database:
        # Remove test users
        mongodb.sync_database.users.delete_many({"email": {"$regex": ".*@example.com"}})
        # Remove test sessions
        mongodb.sync_database.sessions.delete_many({})
        # Remove test conversations and messages
        test_users = mongodb.sync_database.users.find({"email": {"$regex": ".*@example.com"}})
        for user in test_users:
            user_id = str(user["_id"])
            # Delete conversations and their messages
            convs = mongodb.sync_database.conversations.find({"user_id": user_id})
            for conv in convs:
                mongodb.sync_database.messages.delete_many({"conversation_id": str(conv["_id"])})
            mongodb.sync_database.conversations.delete_many({"user_id": user_id})


if __name__ == "__main__":
    # Run tests
    print("Running Authentication Tests...")
    auth_test = TestAuthentication()

    cleanup_test_data()
    auth_test.test_register_user()
    print("✓ User registration test passed")

    cleanup_test_data()
    auth_test.test_login_user()
    print("✓ User login test passed")

    cleanup_test_data()
    auth_test.test_get_current_user()
    print("✓ Get current user test passed")

    cleanup_test_data()
    auth_test.test_invalid_login()
    print("✓ Invalid login test passed")

    print("\nRunning Conversation Tests...")
    conv_test = TestConversations()

    cleanup_test_data()
    conv_test.test_create_conversation()
    print("✓ Create conversation test passed")

    cleanup_test_data()
    conv_test.test_get_conversations()
    print("✓ Get conversations test passed")

    cleanup_test_data()
    conv_test.test_add_message_to_conversation()
    print("✓ Add message test passed")

    cleanup_test_data()
    conv_test.test_get_conversation_with_messages()
    print("✓ Get conversation with messages test passed")

    cleanup_test_data()
    conv_test.test_delete_conversation()
    print("✓ Delete conversation test passed")

    # Final cleanup
    cleanup_test_data()
    print("\n✅ All tests passed!")