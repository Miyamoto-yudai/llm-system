#!/bin/bash

echo "フロントエンド依存関係をインストール中..."

cd llm-client

# クリーンアップ
echo "古い依存関係をクリーンアップ中..."
rm -rf node_modules package-lock.json

# 基本パッケージ
echo "React関連をインストール中..."
npm install react@^18.2.0 react-dom@^18.2.0

echo "ルーティングをインストール中..."
npm install react-router-dom@^6.10.0

echo "UIライブラリをインストール中..."
npm install clsx@^1.2.1
npm install react-icons@^4.11.0
npm install react-hot-toast@^2.4.1

echo "HTTP通信ライブラリをインストール中..."
npm install axios@^1.3.2

echo "認証関連をインストール中..."
npm install js-cookie@^3.0.5
npm install @types/js-cookie@^3.0.4

echo "Google認証をインストール中..."
npm install @react-oauth/google@^0.11.1

echo "その他の依存関係をインストール中..."
npm install body-parser@^1.20.2 express@^4.19.2

echo "開発依存関係をインストール中..."
npm install -D vite@^4.1.0 @vitejs/plugin-react@^3.1.0
npm install -D typescript@^4.9.3 @types/react@^18.0.27 @types/react-dom@^18.0.10
npm install -D tailwindcss@^3.2.6 postcss@^8.4.21 autoprefixer@^10.4.13
npm install -D eslint@^8.33.0 prettier@^2.8.4

echo ""
echo "✅ インストール完了！"
echo ""
echo "起動方法:"
echo "  cd llm-client"
echo "  npm run dev"