# クイックスタートガイド

## 必要なソフトウェア
- Python 3.9以上
- Node.js 16以上
- MongoDB

## セットアップ手順

### 1. 依存関係のインストール

#### バックエンド
```bash
cd llm-server
pip install -r requirements.txt
```

#### フロントエンド
```bash
cd llm-client
npm install
```

もし`npm install`でエラーが出る場合:
```bash
# node_modulesをクリーンアップ
rm -rf node_modules package-lock.json

# 必要なパッケージを個別にインストール
npm install react react-dom
npm install axios clsx js-cookie
npm install react-icons react-hot-toast
npm install @react-oauth/google
npm install react-router-dom
```

### 2. 環境変数の設定

#### バックエンド (.env)
`llm-server/.env`を作成:
```env
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=llm_legal_system
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Google OAuth (オプション)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

#### フロントエンド (.env)
`llm-client/.env`を作成:
```env
REACT_APP_API_URL=http://localhost:8080
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
```

### 3. MongoDBの起動

#### macOS
```bash
brew services start mongodb-community
```

#### Ubuntu/Linux
```bash
sudo systemctl start mongod
```

### 4. サーバーの起動

#### 方法1: スタートアップスクリプトを使用
```bash
./startup.sh
```

#### 方法2: 手動で起動

Terminal 1 - バックエンド:
```bash
cd llm-server
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

Terminal 2 - フロントエンド:
```bash
cd llm-client
npm run dev
```

### 5. アクセス
- フロントエンド: http://localhost:5173
- API ドキュメント: http://localhost:8080/docs

## トラブルシューティング

### エラー: "cannot import name '_QUERY_OPTIONS'"
```bash
cd llm-server
pip uninstall motor pymongo -y
pip install pymongo==4.5.0 motor==3.3.2
```

### エラー: "Module not found"
```bash
cd llm-server
pip install -r requirements.txt
```

### npm installが失敗する
```bash
cd llm-client
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### MongoDBに接続できない
```bash
# MongoDBの状態確認
brew services list  # macOS
sudo systemctl status mongod  # Linux

# MongoDBを再起動
brew services restart mongodb-community  # macOS
sudo systemctl restart mongod  # Linux
```

## 機能の使い方

1. **ゲストモード**: そのまま使用可能（会話履歴は保存されない）
2. **ユーザー登録**: 「ログイン/新規登録」からアカウント作成
3. **Google認証**: Googleボタンでワンクリックログイン（要設定）
4. **会話履歴**: ログイン後、左サイドバーで過去の会話を管理

## 注意事項
- 初回起動時はデータベースのインデックス作成に少し時間がかかります
- Google認証を使用する場合は、Google Cloud Consoleでの設定が必要です（GOOGLE_AUTH_SETUP.md参照）