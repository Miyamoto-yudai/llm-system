# Google OAuth認証セットアップガイド

## 概要
このシステムでは、メールアドレス/パスワード認証に加えて、Google OAuth2.0認証を実装しています。

## セットアップ手順

### 1. Google Cloud Consoleでの設定

#### 1.1 プロジェクト作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）

#### 1.2 OAuth 2.0 クライアントIDの作成
1. 左メニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuthクライアントID」を選択
3. 初回の場合は「同意画面を構成」から設定:
   - ユーザータイプ: 「外部」を選択
   - アプリ名: 「法律相談LawFlow」
   - ユーザーサポートメール: 自分のメールアドレス
   - 承認済みドメイン: 本番環境のドメイン（あれば）
   - デベロッパー連絡先情報: 自分のメールアドレス

#### 1.3 OAuth クライアントの設定
1. アプリケーションの種類: 「ウェブアプリケーション」
2. 名前: 「LawFlow Web Client」
3. 承認済みのJavaScript生成元:
   ```
   http://localhost:5173
   http://localhost:8080
   ```
   本番環境の場合は以下も追加:
   ```
   https://yourdomain.com
   ```

4. 承認済みのリダイレクトURI:
   ```
   http://localhost:8080/api/auth/google/callback
   ```
   本番環境の場合は以下も追加:
   ```
   https://yourdomain.com/api/auth/google/callback
   ```

5. 「作成」をクリック
6. 表示されたクライアントIDとクライアントシークレットをメモ

### 2. バックエンドの設定

#### 2.1 環境変数の設定
`llm-server/.env`ファイルに以下を追加:

```env
# Google OAuth
GOOGLE_CLIENT_ID=あなたのクライアントID
GOOGLE_CLIENT_SECRET=あなたのクライアントシークレット
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

#### 2.2 依存パッケージのインストール
```bash
cd llm-server
pip install -r requirements.txt
```

### 3. フロントエンドの設定

#### 3.1 環境変数の設定
`llm-client/.env`ファイルに以下を追加:

```env
REACT_APP_GOOGLE_CLIENT_ID=あなたのクライアントID
```

#### 3.2 依存パッケージのインストール
```bash
cd llm-client
npm install
```

### 4. 起動確認

#### 4.1 MongoDBの起動
```bash
# macOS
brew services start mongodb-community

# Ubuntu
sudo systemctl start mongod
```

#### 4.2 バックエンドの起動
```bash
cd llm-server
uvicorn src.llm_server.main:app --host 0.0.0.0 --port 8080 --reload
```

#### 4.3 フロントエンドの起動
```bash
cd llm-client
npm run dev
```

#### 4.4 動作確認
1. http://localhost:5173 にアクセス
2. 「ログイン/新規登録」ボタンをクリック
3. 「Googleでログイン」ボタンが表示されることを確認
4. クリックしてGoogleアカウントでログインできることを確認

## 機能説明

### メール/パスワード認証
- 従来通りのメールアドレスとパスワードでの認証
- パスワードは8文字以上必須
- bcryptでハッシュ化して保存

### Google OAuth認証
- ワンクリックでGoogleアカウントログイン
- 初回ログイン時は自動的にアカウント作成
- 同じメールアドレスの既存アカウントがある場合は自動連携
- プロフィール画像も取得可能

### セキュリティ
- OAuth2.0標準プロトコル準拠
- HTTPSでの通信推奨（本番環境必須）
- JWTトークンによるセッション管理
- リフレッシュトークンサポート

## トラブルシューティング

### Googleログインボタンが動作しない
1. Google Cloud ConsoleでクライアントIDが正しく設定されているか確認
2. 環境変数が正しく設定されているか確認
3. リダイレクトURIが正しく設定されているか確認

### 「認証に失敗しました」エラー
1. Google Cloud ConsoleでOAuth同意画面が設定されているか確認
2. クライアントシークレットが正しいか確認
3. MongoDBが起動しているか確認

### CORS エラー
1. バックエンドのCORS設定を確認（main.py）
2. フロントエンドのAPI URLが正しいか確認

## 本番環境への移行

### 1. HTTPSの設定
- SSL証明書を取得（Let's Encrypt推奨）
- NginxまたはApacheでリバースプロキシ設定

### 2. 環境変数の更新
```env
# バックエンド
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback
FRONTEND_URL=https://yourdomain.com

# フロントエンド
REACT_APP_API_URL=https://yourdomain.com/api
```

### 3. Google Cloud Consoleの更新
- 承認済みJavaScript生成元に本番URLを追加
- リダイレクトURIに本番URLを追加

### 4. セキュリティ強化
- JWT_SECRET_KEYを強力なランダム文字列に変更
- MongoDBのアクセス制御設定
- ファイアウォール設定

## 注意事項

- 開発環境では`localhost`を使用しますが、`127.0.0.1`では動作しない場合があります
- Google OAuthは中国など一部の国では利用できません
- 無料のGoogle Cloud利用枠で十分運用可能です（月間数万リクエスト程度）