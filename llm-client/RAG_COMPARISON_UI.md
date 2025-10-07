# RAG比較UI セットアップガイド

このドキュメントでは、RAG比較検証モードのUI機能について説明します。

## 概要

RAG比較検証モードでは、RAGあり/なしの罪名予測・量刑予測の結果を並列で比較できます。

## 新規追加されたファイル

### 1. フロントエンド

- **[src/hooks/useRagComparisonSocket.ts](src/hooks/useRagComparisonSocket.ts)**: RAG比較用WebSocketフック
- **[src/components/RagComparisonMode.tsx](src/components/RagComparisonMode.tsx)**: RAG比較モードのUIコンポーネント

### 2. 更新されたファイル

- **[src/App.tsx](src/App.tsx)**: `/comparison/rag`ルートを追加
- **[src/components/ComparisonMode.tsx](src/components/ComparisonMode.tsx)**: RAG比較モードへのリンク追加

## 環境変数の設定

### バックエンド（llm-server/.env）

```env
# RAG機能の有効化
ENABLE_RAG=true

# OpenAI Vector Store ID
VECTOR_STORE_ID=vs_687714fd39988191abdeacacb3153b8d

# RAG強制モード（オプション）
RAG_ONLY_MODE=false

# 比較モードの有効化
ENABLE_COMPARISON_MODE=true
```

### フロントエンド（llm-client/.env）

```env
# 比較モードの有効化
VITE_COMPARISON_MODE_ENABLED=true

# APIのURL
VITE_API_URL=http://localhost:8000
```

## 使用方法

### 1. 比較モードへのアクセス

比較モードには2種類あります：

#### a. データあり/なし比較モード（既存）
- URL: `http://localhost:5173/comparison`
- 比較対象: 罪名予測テーブル使用 vs LLMのみ

#### b. RAG比較モード（新規）
- URL: `http://localhost:5173/comparison/rag`
- 比較対象: RAGあり（判例参照） vs RAGなし（通常モード）

### 2. 画面の切り替え

各比較モード画面のヘッダーに、もう一方のモードへの切り替えリンクがあります：

- **データあり/なし比較モード** → 「RAG比較モードに切り替え」リンク
- **RAG比較モード** → 「データあり/なし比較モードに切り替え」リンク

### 3. RAG比較モードの特徴

#### 画面構成

```
┌────────────────────────────────────────────────────────┐
│ Header                                                  │
│ - RAG比較検証モード                                     │
│ - 現在の応答タイプ表示（罪名予測/量刑予測など）         │
│ - モード切り替えリンク                                  │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐          │
│  │ RAGあり         │    │ RAGなし         │          │
│  │ (判例参照)      │    │ (通常モード)    │          │
│  │                 │    │                 │          │
│  │ メッセージ表示  │    │ メッセージ表示  │          │
│  │                 │    │                 │          │
│  └─────────────────┘    └─────────────────┘          │
│                                                         │
├────────────────────────────────────────────────────────┤
│ 入力エリア                                              │
│ - クイックテンプレート選択                              │
│ - テキスト入力                                          │
│ - 送信ボタン                                            │
├────────────────────────────────────────────────────────┤
│ 比較統計                                                │
│ - RAGあり: 深掘り質問回数、RAG使用回数                  │
│ - RAGなし: 深掘り質問回数                               │
└────────────────────────────────────────────────────────┘
```

#### 機能

1. **並列比較**: 同じ質問をRAGあり/なしで同時に処理
2. **リアルタイムストリーミング**: 両方の応答をリアルタイムで表示
3. **応答タイプ表示**: 現在の処理タイプ（罪名予測/量刑予測など）を表示
4. **統計表示**: 各モードの深掘り質問回数やRAG使用回数を表示
5. **エクスポート**: 比較結果をJSON形式でダウンロード

## エクスポートデータの形式

```json
{
  "timestamp": "2025-01-15T10:30:00.000Z",
  "comparison": {
    "with_rag": [
      {"speakerId": 1, "text": "ユーザーメッセージ", "timestamp": 1234567890},
      {"speakerId": 0, "text": "アシスタント応答", "timestamp": 1234567891}
    ],
    "without_rag": [
      {"speakerId": 1, "text": "ユーザーメッセージ", "timestamp": 1234567890},
      {"speakerId": 0, "text": "アシスタント応答", "timestamp": 1234567892}
    ]
  },
  "statistics": {
    "with_rag": {
      "total_messages": 10,
      "clarifying_questions": 2,
      "rag_indicators": 3
    },
    "without_rag": {
      "total_messages": 10,
      "clarifying_questions": 3
    }
  },
  "response_type": "predict_crime_and_punishment"
}
```

## WebSocket通信

### エンドポイント

- **RAG比較モード**: `ws://localhost:8000/ws/comparison/rag`
- **データあり/なし比較モード**: `ws://localhost:8000/ws/comparison`

### メッセージ形式

#### クライアント → サーバー

```json
{
  "messages": [
    {"speakerId": 1, "text": "暴行事件の罪名と量刑を予測してください"}
  ]
}
```

#### サーバー → クライアント

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

// 処理開始
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

// 完了
{
  "type": "end",
  "with_rag": "完全な応答（RAGあり）",
  "without_rag": "完全な応答（RAGなし）"
}

// エラー
{
  "type": "error",
  "message": "エラーメッセージ"
}
```

## トラブルシューティング

### RAG比較モードにアクセスできない

1. `.env`ファイルで`VITE_COMPARISON_MODE_ENABLED=true`が設定されているか確認
2. フロントエンドを再起動

### エラーメッセージ「RAG機能が有効になっていません」

1. バックエンドの`.env`で`ENABLE_RAG=true`を設定
2. `VECTOR_STORE_ID`が正しく設定されているか確認
3. バックエンドを再起動

### 比較結果が表示されない

1. WebSocketが正常に接続されているか確認（画面上の接続状態表示）
2. ブラウザのコンソールでエラーを確認
3. バックエンドのログを確認

### RAGの結果が通常モードと変わらない

1. Vector Storeに判例データが正しくアップロードされているか確認
2. `RAG_ONLY_MODE`の設定を確認（`true`にすると、LLMの一般知識を使用しない）

## 開発時のヒント

### デバッグ

ブラウザの開発者ツールのコンソールで、WebSocket通信のログを確認できます：

```javascript
// コンソールに出力されるログ
"RAG Comparison WebSocket connected"
"System message: RAG比較モードで接続しました"
{type: "start", with_rag: true, without_rag: true, response_type: "predict_crime_and_punishment"}
```

### カスタマイズ

- **色の変更**: `ComparisonChat.tsx`の`bgColor`、`borderColor`、`titleBgColor`を編集
- **統計項目の追加**: `RagComparisonMode.tsx`の統計セクションを編集
- **テンプレートの追加**: `QuickTemplates.tsx`を編集

## まとめ

RAG比較検証モードを使用することで、判例参照の有無による予測精度の違いを視覚的に比較・評価できます。エクスポート機能を活用して、複数の比較結果を収集・分析することも可能です。
