# 深掘り質問機能の改善内容

## 実装した機能

### 1. RAGシステムの実装
- **embedding.py**: OpenAI APIを使用したテキストembedding生成機能
- **rag_loader.py**: 罪名予測テーブルと量刑予測ヒアリングシートからRAGデータを生成
- **chat.py改善**: RAGを使用して関連する質問項目を検索し、複数の深掘り質問を生成

### 2. 改善された深掘り質問機能
- 初回の相談時に、5-7個の重要な質問をリスト形式で提示
- 罪名予測テーブルと量刑予測ヒアリングシートの内容を参照
- RAGが利用できない場合はフォールバック処理を使用

## セットアップ方法

### 1. 依存関係のインストール
```bash
pip install tiktoken
```

### 2. OpenAI APIキーの設定
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 3. RAGデータの生成（初回のみ）
```bash
python -m src.rag_loader
```
これにより、`rag_data/`ディレクトリに.refファイルが生成されます。

## 使用方法

### テストスクリプトの実行
```bash
python test_clarifying_questions.py
```

### 通常の使用
```python
from src.chat import reply

# 初回の相談（深掘り質問が返される）
hist = [{"role": "user", "content": "自動車事故です、どのような罪にとわれるでしょうか？"}]
response = reply(hist)

# 深掘り質問への回答後（具体的な回答が返される）
hist.append({"role": "assistant", "content": response})
hist.append({"role": "user", "content": "車同士で交差点です。相手にけがはありません。"})
response2 = reply(hist)
```

## ファイル構成

```
llm-server/
├── src/
│   ├── chat.py                 # 改善されたチャット機能（RAG対応）
│   ├── embedding.py             # 新規：embedding生成機能
│   ├── rag_loader.py           # 新規：RAGデータローダー
│   └── gen/
│       └── rag.py              # 既存のRAGユーティリティ
├── rag_data/                   # RAGデータ保存ディレクトリ（自動生成）
│   ├── *.ref                   # embedding済みの質問データ
│   └── metadata.json           # メタデータ
├── 罪名予測テーブル/           # 参照データ
├── 量刑予測ヒアリングシート/   # 参照データ
└── test_clarifying_questions.py # テストスクリプト
```

## 改善内容の詳細

### 1. 複数質問の生成
- 従来：1つの質問のみ
- 改善後：5-7個の重要な質問をリスト形式で提示

### 2. データ参照の強化
- 罪名予測テーブルの判断基準（列ヘッダー）を活用
- 量刑予測ヒアリングシートの項目を参照
- RAGによる類似度検索で最も関連する質問を取得

### 3. 質問の品質向上
- 端的で答えやすい質問形式
- 重複する質問を排除
- 相談内容に最も関連する質問を優先

## 注意事項

- OpenAI APIキーが設定されていない場合、RAG機能は無効化され、フォールバック処理が使用されます
- RAGデータの生成には時間がかかる場合があります（質問数によって数分程度）
- 初回実行時はRAGデータが存在しないため、フォールバック処理が使用されます