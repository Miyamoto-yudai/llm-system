# RAG機能のセットアップガイド

このドキュメントでは、罪名予測・量刑予測におけるRAG機能の設定と使用方法について説明します。

## 概要

RAG（Retrieval-Augmented Generation）機能を使用することで、判例データベースを参照した高精度な罪名予測・量刑予測が可能になります。

### サポートされる機能

- 罪名予測（RAG使用/未使用）
- 量刑予測（RAG使用/未使用）
- 罪名と量刑の統合予測（RAG使用/未使用）
- RAGあり/なしの比較モード

## 環境変数の設定

`.env`ファイルに以下の環境変数を追加してください：

```env
# RAG機能の有効化
ENABLE_RAG=true

# OpenAI Vector Store ID（判例データがアップロードされたVector StoreのID）
VECTOR_STORE_ID=vs_687714fd39988191abdeacacb3153b8d

# RAG強制モード（オプション、デフォルトはfalse）
# trueの場合、RAGで見つかった情報のみを使用し、LLMの一般知識を使用しない
RAG_ONLY_MODE=false

# 比較モードの有効化（開発環境でのみ使用）
ENABLE_COMPARISON_MODE=true
```

### 環境変数の説明

- **ENABLE_RAG**: RAG機能を有効にするかどうか
- **VECTOR_STORE_ID**: OpenAI Assistants APIで使用するVector StoreのID
- **RAG_ONLY_MODE**: RAG強制モード（資料にない事柄には回答しない）
- **ENABLE_COMPARISON_MODE**: 比較モードを有効にするかどうか

## Vector Storeの準備

RAG機能を使用するには、事前にOpenAI Assistants APIのVector Storeに判例データをアップロードする必要があります。

### Vector Storeの作成手順

1. OpenAI Playgroundまたは APIを使用してVector Storeを作成
2. 判例データ（PDF、テキストファイルなど）をアップロード
3. 生成されたVector Store IDを`.env`ファイルに設定

## 使用方法

### 1. 通常のWebSocketエンドポイント

`/chat`または`/ws/chat`エンドポイントで、メッセージに`use_rag`フラグを含めます：

```json
{
  "messages": [
    {"speakerId": 1, "text": "相談内容..."}
  ],
  "genre": "criminal",
  "use_rag": true
}
```

### 2. RAG比較モード

`/ws/comparison/rag`エンドポイントを使用すると、RAGあり/なしの結果を並列で取得できます：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/comparison/rag');

ws.onopen = () => {
  ws.send(JSON.stringify({
    messages: [
      {speakerId: 1, text: '暴行事件の量刑を予測してください'}
    ]
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'chunk') {
    console.log('RAGあり:', data.with_rag);
    console.log('RAGなし:', data.without_rag);
  } else if (data.type === 'end') {
    console.log('完了');
    console.log('最終結果（RAGあり）:', data.with_rag);
    console.log('最終結果（RAGなし）:', data.without_rag);
  }
};
```

### 3. データあり/なしの比較モード

既存の`/ws/comparison`エンドポイントは、データテーブルあり/なしの比較を提供します：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/comparison');
// 使用方法は同じ
```

## API仕様

### WebSocketメッセージ形式

#### クライアント → サーバー

```json
{
  "messages": [
    {"speakerId": 1, "text": "ユーザーメッセージ"},
    {"speakerId": 2, "text": "アシスタントメッセージ"}
  ],
  "genre": "criminal",  // オプション: "criminal", "traffic", "violence", etc.
  "use_rag": true       // オプション: RAGを使用するか（デフォルトはfalse）
}
```

#### サーバー → クライアント（通常モード）

```json
// 開始通知
{"text": "<start>"}

// チャンク（ストリーミング）
{"text": "応答テキストの一部..."}

// 終了通知
{"text": "<end>"}
```

#### サーバー → クライアント（RAG比較モード）

```json
// システムメッセージ
{
  "type": "system",
  "message": "RAG比較モードで接続しました"
}

// ウェルカムメッセージ
{
  "type": "welcome",
  "with_rag": "こんにちは。ご相談やご質問があればお気軽にお知らせください。",
  "without_rag": "こんにちは。ご相談やご質問があればお気軽にお知らせください。"
}

// 開始通知
{
  "type": "start",
  "with_rag": true,
  "without_rag": true,
  "response_type": "predict_crime_and_punishment"
}

// チャンク（ストリーミング）
{
  "type": "chunk",
  "with_rag": "RAGありの応答の一部...",
  "without_rag": "RAGなしの応答の一部..."
}

// 終了通知
{
  "type": "end",
  "with_rag": "RAGありの完全な応答",
  "without_rag": "RAGなしの完全な応答"
}

// エラー
{
  "type": "error",
  "message": "エラーメッセージ"
}
```

## 実装の詳細

### アーキテクチャ

```
┌─────────────────────┐
│  クライアント        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  WebSocketエンドポイント │
│  - /chat            │
│  - /ws/chat         │
│  - /ws/comparison/rag │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  chat.py            │
│  - reply()          │
│  - predict_*()      │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐  ┌──────────────┐
│通常処理  │  │ RAG処理       │
│(LLM)    │  │ (rag_manager)│
└─────────┘  └──────┬───────┘
                    │
                    ▼
            ┌────────────────┐
            │OpenAI Assistants│
            │File Search API  │
            └────────────────┘
```

### 主要なファイル

1. **[llm-server/src/rag_manager.py](llm-server/src/rag_manager.py)**
   - RAG機能の中核
   - OpenAI Assistants APIのラッパー
   - 罪名予測・量刑予測用のAssistantを管理

2. **[llm-server/src/config.py](llm-server/src/config.py)**
   - 環境変数の管理
   - RAG関連の設定

3. **[llm-server/src/chat.py](llm-server/src/chat.py)**
   - RAG版の予測関数
   - `predict_crime_and_punishment(use_rag=True)`

4. **[llm-server/src/predict_crime_type.py](llm-server/src/predict_crime_type.py)**
   - RAG版の罪名予測
   - `answer(use_rag=True)`

5. **[llm-server/src/api/comparison_routes.py](llm-server/src/api/comparison_routes.py)**
   - RAG比較エンドポイント
   - `/ws/comparison/rag`

## トラブルシューティング

### RAG機能が動作しない

1. `.env`ファイルで`ENABLE_RAG=true`が設定されているか確認
2. `VECTOR_STORE_ID`が正しく設定されているか確認
3. OpenAI APIキーが有効か確認
4. Vector Storeに判例データがアップロードされているか確認

### エラーメッセージ

- **"RAG機能が有効になっていません"**: `ENABLE_RAG=true`を設定してください
- **"VECTOR_STORE_IDが設定されていません"**: `.env`にVector Store IDを設定してください
- **"RAG prediction failed"**: Vector StoreのIDが無効、またはOpenAI APIのエラー

## サンプルコード参照

実装の参考として、以下のサンプルコードを確認してください：

- `罪名予測_GPT_RAG.py`: 罪名予測のRAG実装例
- `量刑予測_GPT_RAG.py`: 量刑予測のRAG実装例

これらのサンプルコードのプロンプトとロジックを基に、本システムのRAG機能が実装されています。

## まとめ

RAG機能を使用することで、判例データベースを参照した高精度な法律相談が可能になります。比較モードを活用して、RAGあり/なしの精度差を評価することもできます。
