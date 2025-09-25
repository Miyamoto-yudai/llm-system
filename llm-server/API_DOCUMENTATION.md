# API ドキュメント

## 概要
このAPIは、法律相談チャットボットシステムのバックエンドです。ユーザー認証、セッション管理、会話履歴の保存・取得機能を提供します。

## ベースURL
```
http://localhost:8080
```

## 認証
JWTトークンベースの認証を使用します。ログイン後に取得したトークンを、Authorizationヘッダーに含めてリクエストしてください。

```
Authorization: Bearer <token>
```

## エンドポイント

### 認証 (Authentication)

#### ユーザー登録
```
POST /api/auth/register
```

リクエストボディ:
```json
{
  "username": "string (3-50文字)",
  "email": "email@example.com",
  "password": "string (8文字以上)"
}
```

レスポンス:
```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "username": "string",
    "email": "email@example.com",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
  }
}
```

#### ログイン
```
POST /api/auth/login
```

リクエストボディ:
```json
{
  "email": "email@example.com",
  "password": "string"
}
```

レスポンス: 登録と同じ形式

#### ログアウト
```
POST /api/auth/logout
```
認証必須

#### 現在のユーザー情報取得
```
GET /api/auth/me
```
認証必須

#### アカウント削除
```
DELETE /api/auth/account
```
認証必須

### 会話管理 (Conversations)

#### 会話一覧取得
```
GET /api/conversations?skip=0&limit=20
```
認証必須

パラメータ:
- skip: スキップする件数 (デフォルト: 0)
- limit: 取得件数 (デフォルト: 20、最大: 100)

レスポンス:
```json
[
  {
    "id": "conversation_id",
    "title": "会話タイトル",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "message_count": 10
  }
]
```

#### 新規会話作成
```
POST /api/conversations
```
認証必須

リクエストボディ:
```json
{
  "title": "会話タイトル (オプション)"
}
```

#### 会話詳細取得（メッセージ含む）
```
GET /api/conversations/{conversation_id}
```
認証必須

レスポンス:
```json
{
  "id": "conversation_id",
  "title": "会話タイトル",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "messages": [
    {
      "id": "message_id",
      "role": "user|assistant",
      "content": "メッセージ内容",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### 会話にメッセージ追加
```
POST /api/conversations/{conversation_id}/messages
```
認証必須

リクエストボディ:
```json
{
  "role": "user|assistant",
  "content": "メッセージ内容"
}
```

#### 会話タイトル更新
```
PUT /api/conversations/{conversation_id}
```
認証必須

リクエストボディ:
```json
{
  "title": "新しいタイトル"
}
```

#### 会話削除
```
DELETE /api/conversations/{conversation_id}
```
認証必須

### WebSocket エンドポイント

#### 通常のチャット（認証なし）
```
ws://localhost:8080/chat?token=<optional_token>
```

トークンを提供した場合、会話履歴が自動保存されます。

#### 認証付きチャット
```
ws://localhost:8080/ws/chat?token=<required_token>&conversation_id=<optional>
```

パラメータ:
- token: JWT認証トークン（必須）
- conversation_id: 既存の会話を継続する場合のID（オプション）

WebSocketメッセージ形式:

送信（クライアント → サーバー）:
```json
{
  "messages": [
    {"speakerId": 1, "text": "ユーザーメッセージ"},
    {"speakerId": 0, "text": "アシスタントメッセージ"}
  ]
}
```

履歴リクエスト:
```json
{
  "type": "history_request"
}
```

受信（サーバー → クライアント）:

会話ID通知:
```json
{
  "type": "conversation_id",
  "conversation_id": "id"
}
```

履歴:
```json
{
  "type": "history",
  "messages": [
    {"role": "user", "content": "内容"},
    {"role": "assistant", "content": "内容"}
  ]
}
```

チャット応答:
```json
{"text": "<start>"}  // 応答開始
{"text": "応答テキスト"}  // ストリーミング応答
{"text": "<end>"}  // 応答終了
```

## エラーレスポンス

```json
{
  "detail": "エラーメッセージ"
}
```

HTTPステータスコード:
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## 環境設定

`.env`ファイルに以下の環境変数を設定してください:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE=llm_legal_system

# JWT
JWT_SECRET_KEY=your_secret_key_here_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
```

## セットアップ手順

1. 依存パッケージのインストール:
```bash
pip install -r requirements.txt
```

2. MongoDBの起動:
```bash
mongod
```

3. 環境変数の設定:
```bash
cp .env.example .env
# .envファイルを編集して必要な値を設定
```

4. サーバーの起動:
```bash
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

## データベース構造

### Collections

#### users
- _id: ObjectId
- username: string (unique)
- email: string (unique)
- password_hash: string
- created_at: datetime
- updated_at: datetime
- is_active: boolean

#### sessions
- _id: ObjectId
- user_id: string
- token: string (unique)
- created_at: datetime
- expires_at: datetime
- ip_address: string (optional)
- user_agent: string (optional)

#### conversations
- _id: ObjectId
- user_id: string
- title: string
- created_at: datetime
- updated_at: datetime
- metadata: object

#### messages
- _id: ObjectId
- conversation_id: string
- role: string ("user" | "assistant")
- content: string
- created_at: datetime
- metadata: object