#!/usr/bin/env python3
"""
Test script to verify the conversation creation functionality
"""

import asyncio
import json
import websocket
import time

def test_guest_chat():
    """Test chat as guest (should not create conversation)"""
    print("Testing guest chat...")
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:8080/chat")

    # Receive welcome message
    while True:
        data = ws.recv()
        msg = json.loads(data)
        print(f"Received: {msg}")
        if msg.get('text') == '<end>':
            break

    # Send a test message
    test_message = [
        {"speakerId": 1, "text": "逮捕されたらどうすればいいですか？"}
    ]
    ws.send(json.dumps(test_message))

    # Receive response
    while True:
        data = ws.recv()
        msg = json.loads(data)
        print(f"Response: {msg}")
        if msg.get('text') == '<end>':
            break

    ws.close()
    print("Guest chat test completed\n")

def test_title_generation():
    """Test title generation from user message"""
    from src.utils.title_generator import generate_conversation_title

    test_cases = [
        ("逮捕されたらどうすればいいですか？", "逮捕に関する相談"),
        ("示談金の相場を教えてください", "示談についての相談"),
        ("飲酒運転で捕まってしまいました", "飲酒運転について"),
        ("これは短いメッセージです", "これは短いメッセージです"),
        ("非常に長いメッセージで、タイトルとして使用するには長すぎる内容を含んでいます。このような場合は省略されるべきです。", None)
    ]

    print("Testing title generation...")
    for message, expected in test_cases:
        generated = generate_conversation_title(message)
        print(f"Input: {message[:50]}...")
        print(f"Generated: {generated}")
        if expected:
            print(f"Expected: {expected}")
            print(f"Match: {generated == expected}")
        print()

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'llm-server'))

    # Test title generation
    test_title_generation()

    # Test WebSocket (optional)
    try:
        test_guest_chat()
    except Exception as e:
        print(f"WebSocket test failed: {e}")
        print("Make sure the server is running on port 8080")