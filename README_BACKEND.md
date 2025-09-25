# バックエンドシステム - セッション管理機能付き

## 概要
法律相談チャットボットのバックエンドに、ユーザー認証とセッション管理、会話履歴保存機能を追加しました。

## 新機能
- ユーザー登録・ログイン機能
- JWT認証によるセッション管理
- 会話履歴の保存・取得
- 会話ごとのメッセージ管理
- 認証付きWebSocketチャット

## セットアップ手順

### 1. MongoDBのインストールと起動

#### macOSの場合:
```bash
# Homebrewでインストール
brew tap mongodb/brew
brew install mongodb-community

# MongoDBを起動
brew services start mongodb-community
```

#### Ubuntuの場合:
```bash
# MongoDBをインストール
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# MongoDBを起動
sudo systemctl start mongod
```

### 2. Python依存パッケージのインストール

```bash
cd llm-server

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集
nano .env  # または好きなエディタで編集
```

以下の環境変数を設定:
- `OPENAI_API_KEY`: OpenAI APIキー
- `JWT_SECRET_KEY`: JWT用の秘密鍵（本番環境では強力なランダム文字列に変更）
- `MONGODB_URL`: MongoDBの接続URL（デフォルト: mongodb://localhost:27017/）

### 4. サーバーの起動

```bash
# 開発環境での起動
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload

# または
python -m uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

## APIの使用例

### 1. ユーザー登録
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. ログイン
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

レスポンスから`access_token`を取得して、以降のリクエストで使用します。

### 3. 会話の作成
```bash
curl -X POST http://localhost:8080/api/conversations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "新しい相談"
  }'
```

### 4. 会話履歴の取得
```bash
curl -X GET http://localhost:8080/api/conversations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. WebSocketでのチャット（認証付き）
```javascript
const token = "YOUR_TOKEN_HERE";
const ws = new WebSocket(`ws://localhost:8080/ws/chat?token=${token}`);

ws.onopen = () => {
    // 会話履歴をリクエスト
    ws.send(JSON.stringify({ type: "history_request" }));

    // メッセージを送信
    ws.send(JSON.stringify({
        messages: [
            { speakerId: 1, text: "質問があります" }
        ]
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

## テストの実行

```bash
# MongoDBが起動していることを確認
# サーバーを起動してから実行

cd llm-server
python tests/test_api.py
```

## ディレクトリ構造

```
llm-server/
├── src/
│   ├── database/          # データベース関連
│   │   ├── connection.py  # MongoDB接続管理
│   │   └── models.py      # データモデル定義
│   ├── auth/              # 認証関連
│   │   └── authentication.py  # JWT認証処理
│   ├── api/               # APIルート
│   │   ├── session_routes.py      # ユーザー認証API
│   │   ├── conversation_routes.py # 会話管理API
│   │   └── websocket_routes.py    # WebSocket処理
│   └── llm_server/
│       └── main.py        # FastAPIメインアプリケーション
├── tests/
│   └── test_api.py        # APIテスト
├── requirements.txt       # Python依存パッケージ
├── .env.example          # 環境変数テンプレート
└── API_DOCUMENTATION.md   # API詳細ドキュメント
```

## トラブルシューティング

### MongoDBに接続できない
```bash
# MongoDBが起動しているか確認
sudo systemctl status mongod  # Linux
brew services list  # macOS

# 手動で起動
mongod --dbpath /path/to/data/db
```

### ポート8080が使用中
```bash
# 使用中のプロセスを確認
lsof -i :8080

# 別のポートを使用
uvicorn src.llm_server.main:app --port 8081
```

### 依存パッケージのエラー
```bash
# pipをアップグレード
pip install --upgrade pip

# 個別にインストール
pip install motor pymongo python-jose passlib
```

## 注意事項

- 本番環境では必ず`JWT_SECRET_KEY`を強力なランダム文字列に変更してください
- MongoDBのアクセス制御を設定することを推奨します
- HTTPS/WSSを使用することを推奨します
- CORSの設定を本番環境に合わせて調整してください

## 今後の改善案

- パスワードリセット機能
- メール認証
- ソーシャルログイン
- レート制限
- ログ管理の強化
- バックアップ機能