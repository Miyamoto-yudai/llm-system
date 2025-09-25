#!/bin/bash

echo "=========================================="
echo "スタートアップスクリプトの動作テスト"
echo "=========================================="

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "1. ディレクトリ構造の確認..."
if [ -d "llm-server" ] && [ -d "llm-client" ]; then
    echo "   ✅ ディレクトリ構造は正常です"
else
    echo "   ❌ llm-server または llm-client ディレクトリが見つかりません"
    exit 1
fi

echo ""
echo "2. Python環境の確認..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 がインストールされています"
    python3 --version
else
    echo "   ❌ Python3 がインストールされていません"
    exit 1
fi

echo ""
echo "3. Node.js環境の確認..."
if command -v npm &> /dev/null; then
    echo "   ✅ npm がインストールされています"
    npm --version
else
    echo "   ❌ npm がインストールされていません"
    exit 1
fi

echo ""
echo "4. バックエンド設定の確認..."
if [ -f "llm-server/.env" ]; then
    echo "   ✅ llm-server/.env が存在します"
    # OpenAI APIキーの存在確認（値は表示しない）
    if grep -q "OPENAI_API_KEY=sk-" "llm-server/.env"; then
        echo "   ✅ OpenAI APIキーが設定されています"
    else
        echo "   ⚠️  OpenAI APIキーが設定されていない可能性があります"
    fi
else
    echo "   ❌ llm-server/.env が見つかりません"
fi

if [ -f "llm-server/requirements.txt" ]; then
    echo "   ✅ requirements.txt が存在します"
else
    echo "   ❌ requirements.txt が見つかりません"
fi

echo ""
echo "5. フロントエンド設定の確認..."
if [ -f "llm-client/.env" ]; then
    echo "   ✅ llm-client/.env が存在します"
else
    echo "   ❌ llm-client/.env が見つかりません"
fi

if [ -f "llm-client/package.json" ]; then
    echo "   ✅ package.json が存在します"
else
    echo "   ❌ package.json が見つかりません"
fi

if [ -d "llm-client/node_modules" ]; then
    echo "   ✅ node_modules が存在します"
else
    echo "   ⚠️  node_modules が存在しません（npm install が必要）"
fi

echo ""
echo "6. Python仮想環境の確認..."
cd llm-server
if [ -d "venv" ] || [ -d "venv_new" ]; then
    echo "   ✅ 仮想環境が存在します"

    # 仮想環境をアクティベートして必要なパッケージの確認
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source venv_new/bin/activate
    fi

    # 主要なパッケージの確認
    echo "   主要パッケージの確認:"
    for pkg in fastapi uvicorn openai pymongo; do
        if python -c "import $pkg" 2>/dev/null; then
            echo "      ✅ $pkg"
        else
            echo "      ❌ $pkg (インストールが必要)"
        fi
    done

    deactivate
else
    echo "   ⚠️  仮想環境が存在しません（作成されます）"
fi

cd ..

echo ""
echo "7. ポート使用状況の確認..."
# ポート8080の確認
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "   ⚠️  ポート 8080 は既に使用中です"
    lsof -Pi :8080 -sTCP:LISTEN
else
    echo "   ✅ ポート 8080 は利用可能です"
fi

# ポート5173の確認
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "   ⚠️  ポート 5173 は既に使用中です"
    lsof -Pi :5173 -sTCP:LISTEN
else
    echo "   ✅ ポート 5173 は利用可能です"
fi

echo ""
echo "=========================================="
echo "テスト完了"
echo ""

# 総合判定
all_good=true
if [ ! -f "llm-server/.env" ]; then
    all_good=false
    echo "❌ llm-server/.env を設定してください"
fi

if [ ! -f "llm-client/.env" ]; then
    all_good=false
    echo "❌ llm-client/.env を設定してください"
fi

if [ ! -d "llm-client/node_modules" ]; then
    echo "⚠️  cd llm-client && npm install を実行してください"
fi

if $all_good; then
    echo "✅ startup.sh を実行する準備ができています！"
    echo ""
    echo "実行コマンド: ./startup.sh"
else
    echo ""
    echo "上記の問題を解決してからstartup.shを実行してください"
fi
echo "=========================================="