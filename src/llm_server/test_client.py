import websocket
import json

# WebSocket サーバーの URL
ws_url = "ws://127.0.0.1/chat"


# 送信する JSON データ
data_to_send = [{"text": "法律相談をしたいです", "speakerId": 1}]

try:
    # WebSocket 接続の確立
    ws = websocket.create_connection(ws_url)

    # JSON データを文字列に変換して送信
    ws.send(json.dumps(data_to_send))

    while True:
        # サーバーからの応答を受信
        response = ws.recv()
        print("Received: '%s'" % response)

        # '<end>' メッセージが送られてきたらループを終了
        if response == "<end>":
            break

except Exception as e:
    print("Error: %s" % e)
finally:
    # 接続を閉じる
    ws.close()
