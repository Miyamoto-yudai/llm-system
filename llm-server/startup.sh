#!/bin/bash

echo "法律相談LawFlow - スタートアップスクリプト"
echo "=================================="

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# MongoDBの起動確認（オプション - ログイン機能を使う場合のみ必要）
echo "1. MongoDBの状態を確認中..."
if command -v mongod &> /dev/null; then
    if pgrep -x "mongod" > /dev/null; then
        echo "   ✅ MongoDBは既に起動しています"
    else
        echo "   ⚠️  MongoDBが起動していません（ログイン機能は使用できません）"
        echo "   ログイン機能を使用する場合は、以下のコマンドでMongoDBを起動してください:"
        echo "   macOS: brew services start mongodb-community"
        echo "   Linux: sudo systemctl start mongod"
    fi
else
    echo "   ⚠️  MongoDBがインストールされていません（ログイン機能は使用できません）"
    echo "   ログイン機能を使用する場合は、インストール方法はGOOGLE_AUTH_SETUP.mdを参照してください"
fi

# バックエンドの起動
echo ""
echo "2. バックエンドサーバーを起動中..."
cd "$SCRIPT_DIR/llm-server"

# 仮想環境の確認と作成
if [ -d "venv" ]; then
    echo "   仮想環境をアクティベート中..."
    source venv/bin/activate
elif [ -d "venv_new" ]; then
    echo "   仮想環境(venv_new)をアクティベート中..."
    source venv_new/bin/activate
else
    echo "   仮想環境が見つかりません。作成中..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 依存関係のインストール
echo "   依存パッケージを確認中..."
pip install -q -r requirements.txt 2>/dev/null || {
    echo "   ⚠️  依存パッケージのインストールに失敗しました"
    echo "   手動でインストールしてください: pip install -r requirements.txt"
}

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "   ⚠️  .envファイルが見つかりません"
    echo "   llm-server/.env.exampleを.envにコピーして設定してください"
    exit 1
fi

# サーバー起動
echo "   バックエンドサーバーを起動します..."
echo "   URL: http://localhost:8080"
python -m uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!

echo "   ✅ バックエンドサーバーを起動しました (PID: $BACKEND_PID)"

# フロントエンドの起動
echo ""
echo "3. フロントエンドサーバーを起動中..."
cd "$SCRIPT_DIR/llm-client"

# Node.jsとnpmの確認
if ! command -v npm &> /dev/null; then
    echo "   ⚠️  npmがインストールされていません"
    echo "   Node.jsをインストールしてください: https://nodejs.org/"
    exit 1
fi

# 依存関係の確認とインストール
if [ ! -d "node_modules" ]; then
    echo "   node_modulesが見つかりません。インストール中..."
    npm install || {
        echo "   ⚠️  npm installに失敗しました"
        exit 1
    }
fi

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "   ⚠️  .envファイルが見つかりません"
    echo "   llm-client/.env.exampleを.envにコピーして設定してください"
    # .env.exampleが存在する場合は自動でコピー
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   .env.exampleから.envを作成しました"
    fi
fi

echo "   フロントエンドサーバーを起動します..."
echo "   URL: http://localhost:5173"
npm run dev &
FRONTEND_PID=$!
echo "   ✅ フロントエンドサーバーを起動しました (PID: $FRONTEND_PID)"

echo ""
echo "=================================="
echo "起動完了！"
echo ""
echo "アクセスURL:"
echo "  フロントエンド: http://localhost:5173"
echo "  バックエンドAPI: http://localhost:8080/docs"
if [ "$ENABLE_COMPARISON_MODE" = "true" ]; then
    echo "  比較モード: http://localhost:5173/comparison"
fi
echo ""
echo "終了するには Ctrl+C を押してください"
echo "=================================="

# 終了時のクリーンアップ処理
cleanup() {
    echo ""
    echo "シャットダウン中..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "  バックエンドサーバーを停止しました"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "  フロントエンドサーバーを停止しました"
    fi
    exit 0
}

# Ctrl+Cでのシグナルをキャッチ
trap cleanup INT TERM

# Keep script running
wait $BACKEND_PID $FRONTEND_PID