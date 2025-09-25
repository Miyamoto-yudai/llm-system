"""
比較モード用のWebSocketルート
同じ入力に対して、データあり（通常モード）とデータなし（LLMのみ）の
2つの処理を並列実行し、結果を比較できるようにする
"""

import json
import logging
import asyncio
from typing import List, Dict, Tuple
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import src.chat as chat_with_data
import src.chat_comparison as chat_without_data


router = APIRouter()

# 比較セッションのログを保存
comparison_logs = []


async def process_with_data(hist: List[Dict]) -> Tuple[str, List[str]]:
    """データテーブルありの処理（通常モード）"""
    chunks = []
    response_text = ""

    try:
        rep = chat_with_data.reply(hist)

        if isinstance(rep, str):
            response_text = rep
            chunks.append(rep)
        else:
            for chunk in rep:
                response_text += chunk
                chunks.append(chunk)
    except Exception as e:
        logging.error(f"Error in process_with_data: {e}")
        response_text = "エラーが発生しました"
        chunks = [response_text]

    return response_text, chunks


async def process_without_data(hist: List[Dict]) -> Tuple[str, List[str]]:
    """データテーブルなしの処理（LLMのみモード）"""
    chunks = []
    response_text = ""

    try:
        rep = chat_without_data.reply_without_data(hist)

        if isinstance(rep, str):
            response_text = rep
            chunks.append(rep)
        else:
            for chunk in rep:
                response_text += chunk
                chunks.append(chunk)
    except Exception as e:
        logging.error(f"Error in process_without_data: {e}")
        response_text = "エラーが発生しました"
        chunks = [response_text]

    return response_text, chunks


@router.websocket("/ws/comparison")
async def websocket_comparison_endpoint(ws: WebSocket):
    """
    比較モード用のWebSocketエンドポイント
    同じ入力に対して2つの処理を実行し、結果を返す
    """
    await ws.accept()

    # セッション開始メッセージ
    await ws.send_json({
        "type": "system",
        "message": "比較モードで接続しました"
    })

    # ウェルカムメッセージを送信
    welcome_msg = chat_with_data.WELCOME_MESSAGE
    await ws.send_json({
        "type": "welcome",
        "with_data": welcome_msg,
        "without_data": welcome_msg
    })

    while True:
        try:
            # クライアントからのメッセージを受信
            json_string = await ws.receive_text()
            data = json.loads(json_string)

            # メッセージタイプの処理
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
                continue

            # 会話履歴の取得
            messages = data.get("messages", [])
            if not messages:
                continue

            # 履歴をchat.py形式に変換
            hist = []
            for msg in messages:
                if msg.get("speakerId") == 1:  # ユーザー
                    hist.append({"role": "user", "content": msg.get('text', '')})
                else:  # アシスタント
                    hist.append({"role": "assistant", "content": msg.get('text', '')})

            # 開始通知
            await ws.send_json({
                "type": "start",
                "with_data": True,
                "without_data": True
            })

            # 2つの処理を並列実行
            try:
                # 非同期で両方の処理を実行
                task_with_data = asyncio.create_task(process_with_data(hist))
                task_without_data = asyncio.create_task(process_without_data(hist))

                # 両方の結果を待つ
                (response_with_data, chunks_with_data), (response_without_data, chunks_without_data) = await asyncio.gather(
                    task_with_data,
                    task_without_data
                )

                # チャンク単位で送信（ストリーミング風に）
                max_chunks = max(len(chunks_with_data), len(chunks_without_data))

                for i in range(max_chunks):
                    chunk_data = {
                        "type": "chunk"
                    }

                    if i < len(chunks_with_data):
                        chunk_data["with_data"] = chunks_with_data[i]

                    if i < len(chunks_without_data):
                        chunk_data["without_data"] = chunks_without_data[i]

                    await ws.send_json(chunk_data)
                    await asyncio.sleep(0.02)  # ストリーミング効果のための小休止

                # 完了通知
                await ws.send_json({
                    "type": "end",
                    "with_data": response_with_data,
                    "without_data": response_without_data
                })

                # 比較ログの保存
                comparison_logs.append({
                    "input": hist[-1]["content"] if hist else "",
                    "response_with_data": response_with_data,
                    "response_without_data": response_without_data,
                    "timestamp": asyncio.get_event_loop().time()
                })

            except Exception as e:
                logging.error(f"Error in comparison processing: {e}")
                await ws.send_json({
                    "type": "error",
                    "message": "処理中にエラーが発生しました"
                })

        except WebSocketDisconnect:
            print("WebSocket disconnected in comparison mode")
            break
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            await ws.send_json({
                "type": "error",
                "message": "無効なメッセージ形式です"
            })
        except Exception as e:
            logging.error(f"Unexpected error in comparison WebSocket: {e}")
            await ws.send_json({
                "type": "error",
                "message": "予期しないエラーが発生しました"
            })
            break


@router.get("/api/comparison/logs")
async def get_comparison_logs():
    """比較ログを取得するエンドポイント（検証用）"""
    return {"logs": comparison_logs}


@router.delete("/api/comparison/logs")
async def clear_comparison_logs():
    """比較ログをクリアするエンドポイント（検証用）"""
    global comparison_logs
    comparison_logs = []
    return {"message": "Logs cleared"}