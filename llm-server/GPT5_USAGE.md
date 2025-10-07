# GPT-5モデル使用ガイド

## 概要

このシステムでは、OpenAIの最新モデルGPT-5シリーズを簡単に使用できるように設定されています。

## GPT-5の特徴

### 利用可能なモデル
- `gpt-5`: 最高性能のモデル（$1.25/1M入力、$10/1M出力）
- `gpt-5-mini`: 中間性能モデル（$0.25/1M入力、$2/1M出力）
- `gpt-5-nano`: 最速・最安モデル（$0.05/1M入力、$0.40/1M出力）

### GPT-5の重要な制約と対策
- **temperatureパラメータは使用不可**（デフォルト1.0に固定）
- カスタムtemperature値を指定するとエラーが発生します
- **対策**: `seed`パラメータを使用することで決定論的な出力を実現
  - 同じseed値 + 同じ入力 → ほぼ同じ出力（再現性あり）
  - 入力が変われば → 異なる出力（会話履歴の変化を確実に反映）
  - システムは自動的にseed=42を使用（変更可能）

### GPT-5専用パラメータ

#### 1. reasoning_effort（推論の深さ）
- `minimal`: 最速応答（推論を最小限に）
- `low`: 簡単なタスク用
- `medium`: 標準（デフォルト、推奨）
- `high`: 複雑な多段階タスク用

#### 2. verbosity（出力の詳細度）
- `low`: 簡潔な出力
- `medium`: 標準（デフォルト）
- `high`: 詳細な出力

#### 3. seed（再現性の確保）
- GPT-5はtemperature=1.0固定のため、seedパラメータで決定論性を確保
- デフォルト値: 42（`config.py`の`SEED_VALUE`で変更可能）
- これにより、同じ質問の繰り返しを防ぎ、会話履歴の変化を確実に反映

## 使用方法

### 1. config.pyでモデルを指定

`llm-server/src/config.py`を開き、`GPT_MODELS`セクションでモデルを変更します：

```python
GPT_MODELS = {
    # メインモデル（高精度が必要な処理用）
    "main": "gpt-5",  # または "gpt-5-mini", "gpt-5-nano"

    # 分類用モデル（応答タイプの判定等）
    "classifier": "gpt-5-nano",  # 高速化優先

    # 質問生成用モデル（深掘り質問の生成等）
    "question_generator": "gpt-5",  # 質問の質を重視

    # ストリーミング対応モデル（リアルタイム応答用）
    "streaming": "gpt-5-mini",

    # Embedding用モデル
    "embedding": "text-embedding-ada-002"
}
```

### 2. GPT-5パラメータの調整（オプション）

必要に応じて、`config.py`の以下の設定を変更できます：

```python
# reasoning_effortの設定
GPT5_REASONING_EFFORT = {
    "main": "medium",
    "classifier": "low",           # 分類は高速化優先
    "question_generator": "high",  # 質問生成は深い推論を使用
    "streaming": "medium"
}

# verbosityの設定
GPT5_VERBOSITY = {
    "main": "medium",
    "classifier": "low",           # 分類は簡潔に
    "question_generator": "medium",
    "streaming": "medium"
}
```

### 3. 推奨設定例

#### ケース1: 深掘り質問の精度を最大化
```python
GPT_MODELS = {
    "question_generator": "gpt-5",  # 最高性能モデル
}

GPT5_REASONING_EFFORT = {
    "question_generator": "high",   # 深い推論
}

GPT5_VERBOSITY = {
    "question_generator": "medium",
}
```

#### ケース2: 高速化優先（コスト削減）
```python
GPT_MODELS = {
    "question_generator": "gpt-5-nano",  # 最速・最安モデル
}

GPT5_REASONING_EFFORT = {
    "question_generator": "minimal",     # 最小限の推論
}

GPT5_VERBOSITY = {
    "question_generator": "low",         # 簡潔な出力
}
```

#### ケース3: バランス型（推奨）
```python
GPT_MODELS = {
    "question_generator": "gpt-5-mini",  # 中間性能
}

GPT5_REASONING_EFFORT = {
    "question_generator": "medium",      # 標準的な推論
}

GPT5_VERBOSITY = {
    "question_generator": "medium",      # 標準的な詳細度
}
```

## 注意事項

1. **モデル切替時の互換性**
   - GPT-4からGPT-5への切替は自動的に処理されます
   - GPT-5ではtemperatureが無視され、reasoning_effortとverbosityが使用されます
   - GPT-4ではtemperatureが使用され、reasoning_effortとverbosityは無視されます

2. **コスト管理**
   - GPT-5は高性能ですが、GPT-4より高価です
   - 用途に応じてgpt-5-nanoやgpt-5-miniの使用を検討してください
   - 分類など単純なタスクにはgpt-5-nanoが最適です

3. **パフォーマンス**
   - reasoning_effort="minimal"は応答速度が大幅に向上します
   - 深掘り質問生成など複雑なタスクではreasoning_effort="high"を推奨します

## トラブルシューティング

### エラー: "temperature does not support X with this model"
- GPT-5シリーズではtemperatureパラメータが使用できません
- `config.create_chat_completion()`関数を使用していることを確認してください
- 直接`client.chat.completions.create()`を使用している箇所がないか確認してください

### 深掘り質問が繰り返される（重要）
**問題**: GPT-5でユーザーの回答を無視して、全く同じ質問を繰り返す

**原因**: GPT-5はtemperature=1.0固定のため、seedパラメータなしでは決定論的な出力が得られない

**解決済**: システムは自動的に`seed=42`を使用するため、この問題は発生しません
- 会話履歴が更新されれば、確実に異なる質問を生成します
- もし問題が発生する場合は、`config.py`の`SEED_VALUE`を別の値（例: 123）に変更してください

### 応答が遅い
- `reasoning_effort`を"low"または"minimal"に変更してください
- より軽量なモデル（gpt-5-nanoやgpt-5-mini）を検討してください

### 質問の質が低い
- `reasoning_effort`を"high"に変更してください
- より高性能なモデル（gpt-5）を使用してください

## 実装の詳細

システムは自動的にモデルを判定し、適切なパラメータを使用します：

- **GPT-5系モデル**: reasoning_effort + verbosity + **seed**
- **GPT-4系モデル**: temperature

この判定は`config.is_gpt5_model()`関数で行われ、全てのAPI呼び出しで自動的に適用されます。

### seedパラメータの重要性

GPT-5はtemperature=1.0固定のため、従来のGPT-4のような決定論的な出力が得られません。これにより以下の問題が発生する可能性がありました：

- 同じ会話履歴に対して、毎回異なる分析結果を返す
- ユーザーの新しい回答を十分に考慮せず、似た質問を繰り返す

**解決策**: `seed`パラメータを追加することで、この問題を解決しました。
- 同じseed + 同じ入力 → ほぼ同じ出力（再現性）
- 入力が変化（会話履歴更新） → 確実に異なる出力

これにより、GPT-5でもGPT-4と同等の決定論的な動作を実現しています。
