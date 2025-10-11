# LLL System (Legal LLM System)

法律相談システム - OpenAI APIを使用した法律相談チャットボットシステム

## 目次
- [システム概要](#システム概要)
- [必要な環境](#必要な環境)
- [セットアップ手順](#セットアップ手順)
- [実行方法](#実行方法)
- [プロジェクト構成](#プロジェクト構成)
- [トラブルシューティング](#トラブルシューティング)
- [追加ドキュメント](#追加ドキュメント)

## システム概要

このシステムは以下の2つのコンポーネントで構成されています:

- **バックエンド (llm-server)**: FastAPIベースのチャットボットエンジン（OpenAI APIとの橋渡し）
- **フロントエンド (llm-client)**: React + Viteベースのユーザーインターフェース

## 必要な環境

### 必須ソフトウェア
- **Python**: 3.9以上
- **Node.js**: 16以上 (推奨: 18以上)
- **npm**: 7以上
- **MongoDB**: 4.4以上 (ログイン機能を使用する場合)

### 必要なアカウント
- **OpenAI API キー**: [OpenAI Platform](https://platform.openai.com/)で取得
- **Google OAuth** (オプション): [Google Cloud Console](https://console.cloud.google.com/)で設定

## セットアップ手順

### ステップ1: リポジトリのクローン

```bash
git clone <repository-url>
cd lll-system
```

### ステップ2: MongoDB のインストールと起動

#### macOS の場合
```bash
# Homebrewを使用してインストール
brew tap mongodb/brew
brew install mongodb-community

# MongoDBを起動
brew services start mongodb-community

# 起動確認
brew services list | grep mongodb
```

#### Ubuntu/Linux の場合
```bash
# MongoDBをインストール
sudo apt-get update
sudo apt-get install -y mongodb

# MongoDBを起動
sudo systemctl start mongod
sudo systemctl enable mongod

# 起動確認
sudo systemctl status mongod
```

#### Windows の場合
[MongoDB公式サイト](https://www.mongodb.com/try/download/community)からインストーラーをダウンロードしてインストール

> **注意**: ログイン機能を使わない場合、MongoDBは必須ではありません（ゲストモードで使用可能）

### ステップ3: バックエンドのセットアップ

#### 3-1. バックエンドディレクトリへ移動
```bash
cd llm-server
```

#### 3-2. Python仮想環境の作成とアクティベート
```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

#### 3-3. 依存パッケージのインストール
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3-4. 環境変数の設定
```bash
# .env.exampleを.envにコピー
cp .env.example .env

# .envファイルを編集
nano .env  # またはお好みのエディタで開く
```

**.env** ファイルの設定内容:
```env
# OpenAI API キー（必須）
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx

# MongoDB設定（ログイン機能を使う場合）
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=llm_legal_system

# JWT設定（ログイン機能を使う場合）
JWT_SECRET_KEY=your_random_secret_key_here_change_this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth（オプション）
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback

# サーバー設定
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
FRONTEND_URL=http://localhost:5173
```

> **重要**:
> - `OPENAI_API_KEY` は必須です
> - `JWT_SECRET_KEY` は本番環境では安全なランダム文字列に変更してください

### ステップ4: フロントエンドのセットアップ

#### 4-1. フロントエンドディレクトリへ移動
```bash
# プロジェクトルートに戻る
cd ..
cd llm-client
```

#### 4-2. Node.jsパッケージのインストール
```bash
npm install
```

エラーが出る場合:
```bash
# キャッシュをクリアして再試行
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 4-3. 環境変数の設定
```bash
# .envファイルを作成（存在しない場合）
nano .env
```

**.env** ファイルの内容:
```env
# バックエンドAPIのURL
VITE_API_URL=http://localhost:8080

# Google OAuth クライアントID（オプション）
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here

# 比較モード有効化（オプション）
VITE_COMPARISON_MODE_ENABLED=true
```

## 実行方法

### 方法1: スタートアップスクリプトを使用（推奨）

プロジェクトルートから実行:
```bash
cd /path/to/lll-system
chmod +x startup.sh  # 初回のみ
./startup.sh
```

このスクリプトは以下を自動的に行います:
- MongoDB の起動確認
- バックエンドサーバーの起動 (http://localhost:8080)
- フロントエンドサーバーの起動 (http://localhost:5173)

終了する場合は `Ctrl+C` を押してください。

### 方法2: 手動で起動

#### ターミナル1: バックエンド
```bash
cd llm-server
source venv/bin/activate  # 仮想環境をアクティベート
python -m uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

#### ターミナル2: フロントエンド
```bash
cd llm-client
npm run dev
```

### アクセスURL

- **フロントエンド**: http://localhost:5173
- **バックエンド API ドキュメント**: http://localhost:8080/docs
- **比較モード** (有効な場合): http://localhost:5173/comparison

## プロジェクト構成

```
lll-system/
├── llm-server/              # バックエンド (FastAPI)
│   ├── src/
│   │   ├── llm_server/      # メインアプリケーション
│   │   │   └── main.py      # FastAPIエントリーポイント
│   │   ├── api/             # APIルート
│   │   ├── auth/            # 認証関連
│   │   ├── database/        # MongoDB接続
│   │   ├── chat.py          # チャット処理
│   │   └── rag_manager.py   # RAG機能
│   ├── requirements.txt     # Python依存パッケージ
│   ├── .env                 # 環境変数 (自分で作成)
│   └── .env.example         # 環境変数のテンプレート
│
├── llm-client/              # フロントエンド (React + Vite)
│   ├── src/
│   │   ├── components/      # Reactコンポーネント
│   │   ├── hooks/           # カスタムフック
│   │   └── App.tsx          # メインアプリケーション
│   ├── package.json         # Node.js依存パッケージ
│   ├── .env                 # 環境変数 (自分で作成)
│   └── vite.config.ts       # Vite設定
│
├── startup.sh               # 自動起動スクリプト
├── README.md                # このファイル
└── .env.example             # 環境変数のテンプレート
```

## トラブルシューティング

### エラー: "OPENAI_API_KEY not found"
```bash
# llm-server/.envファイルが存在し、正しくAPI キーが設定されているか確認
cd llm-server
cat .env | grep OPENAI_API_KEY
```

### エラー: "cannot import name '_QUERY_OPTIONS'"
MongoDB/Motor のバージョン不整合です:
```bash
cd llm-server
source venv/bin/activate
pip uninstall motor pymongo -y
pip install pymongo==4.5.0 motor==3.3.2
```

### エラー: "Module not found" (Python)
```bash
cd llm-server
source venv/bin/activate
pip install -r requirements.txt
```

### エラー: "Module not found" (Node.js)
```bash
cd llm-client
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### MongoDBに接続できない
```bash
# MongoDBの状態を確認
# macOS:
brew services list | grep mongodb

# Linux:
sudo systemctl status mongod

# MongoDBを再起動
# macOS:
brew services restart mongodb-community

# Linux:
sudo systemctl restart mongod
```

### ポートが既に使用されている
```bash
# ポート8080を使用しているプロセスを確認
lsof -i :8080

# ポート5173を使用しているプロセスを確認
lsof -i :5173

# プロセスを終了する場合
kill -9 <PID>
```

### OpenAI API エラー: "Rate limit exceeded"
APIの使用制限に達しています。しばらく待つか、[OpenAI Platform](https://platform.openai.com/)で利用状況を確認してください。

### OpenAI API エラー: "Invalid API key"
APIキーが正しいか確認してください:
```bash
cd llm-server
cat .env | grep OPENAI_API_KEY
```

### フロントエンドが真っ白
```bash
# ブラウザのコンソールを確認 (F12キー)
# バックエンドが起動しているか確認
curl http://localhost:8080/docs
```

## 追加ドキュメント

詳細な情報は以下のドキュメントを参照してください:

- [QUICK_START.md](QUICK_START.md) - クイックスタートガイド
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API仕様
- [GOOGLE_AUTH_SETUP.md](GOOGLE_AUTH_SETUP.md) - Google OAuth設定
- [MODEL_CONFIG.md](MODEL_CONFIG.md) - AIモデル設定
- [README_BACKEND.md](README_BACKEND.md) - バックエンド詳細
- [RAG_SETUP.md](llm-server/RAG_SETUP.md) - RAG機能の設定

## 本番環境へのデプロイ

### Dockerを使用する場合
```bash
# Dockerイメージをビルド
docker build -t lll-system .

# コンテナを起動
docker run -p 80:80 --env-file .env -it lll-system
```

### ECRへプッシュ (AWS)
```bash
./save_to_ecr.sh
```

## ライセンスと著作権

本プロジェクトは[original](https://github.com/KtechB/llm-server)を改変したものです。

## サポート

問題が発生した場合は、以下を確認してください:
1. すべての依存パッケージが正しくインストールされているか
2. 環境変数が正しく設定されているか
3. MongoDBが起動しているか（ログイン機能を使用する場合）
4. OpenAI API キーが有効か
5. ポート8080と5173が利用可能か

それでも解決しない場合は、エラーメッセージとともに開発チームに連絡してください。
