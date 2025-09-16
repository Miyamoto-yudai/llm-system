#!/bin/bash

echo "法律相談LawFlow - スタートアップスクリプト"
echo "=================================="

# MongoDBの起動確認
echo "1. MongoDBの状態を確認中..."
if command -v mongod &> /dev/null; then
    if pgrep -x "mongod" > /dev/null; then
        echo "   ✅ MongoDBは既に起動しています"
    else
        echo "   ⚠️  MongoDBが起動していません"
        echo "   以下のコマンドでMongoDBを起動してください:"
        echo "   macOS: brew services start mongodb-community"
        echo "   Linux: sudo systemctl start mongod"
        exit 1
    fi
else
    echo "   ⚠️  MongoDBがインストールされていません"
    echo "   インストール方法はGOOGLE_AUTH_SETUP.mdを参照してください"
    exit 1
fi

# バックエンドの起動
echo ""
echo "2. バックエンドサーバーを起動中..."
cd llm-server

# 仮想環境の確認
if [ -d "venv" ]; then
    echo "   仮想環境をアクティベート中..."
    source venv/bin/activate
elif [ -d "venv_new" ]; then
    echo "   仮想環境(venv_new)をアクティベート中..."
    source venv_new/bin/activate
fi

# 依存関係のインストール
echo "   依存パッケージを確認中..."
pip install -q -r requirements.txt 2>/dev/null || {
    echo "   ⚠️  依存パッケージのインストールに失敗しました"
    echo "   手動でインストールしてください: pip install -r requirements.txt"
}

# サーバー起動
echo "   バックエンドサーバーを起動します..."
echo "   URL: http://localhost:8080"
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!

echo "   ✅ バックエンドサーバーを起動しました (PID: $BACKEND_PID)"

# フロントエンドの起動
echo ""
echo "3. フロントエンドサーバーを起動中..."
cd ../llm-client

# 依存関係の確認
if [ ! -d "node_modules" ]; then
    echo "   node_modulesが見つかりません。npm installを実行してください:"
    echo "   cd llm-client && npm install"
else
    echo "   フロントエンドサーバーを起動します..."
    echo "   URL: http://localhost:5173"
    npm run dev &
    FRONTEND_PID=$!
    echo "   ✅ フロントエンドサーバーを起動しました (PID: $FRONTEND_PID)"
fi

echo ""
echo "=================================="
echo "起動完了！"
echo ""
echo "アクセスURL:"
echo "  フロントエンド: http://localhost:5173"
echo "  バックエンドAPI: http://localhost:8080/docs"
echo ""
echo "終了するには Ctrl+C を押してください"
echo "=================================="

# Keep script running
wait