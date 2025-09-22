# GPTモデル設定ガイド

## 概要
このプロジェクトのGPTモデル指定は`src/config.py`で一元管理されています。

## モデルの変更方法

### 1. 設定ファイルの場所
```
src/config.py
```

### 2. モデル設定の構造

```python
GPT_MODELS = {
    "main": "gpt-4o",                    # メイン処理用（罪名予測など）
    "classifier": "gpt-4o-mini",          # 相談タイプの分類用
    "question_generator": "gpt-4o-mini",  # 深掘り質問生成用
    "streaming": "gpt-4o-mini",           # ストリーミング応答用
    "embedding": "text-embedding-ada-002" # RAG用のembedding
}
```

### 3. モデルを変更する場合

例：全てのモデルをGPT-3.5に変更したい場合

```python
GPT_MODELS = {
    "main": "gpt-3.5-turbo",
    "classifier": "gpt-3.5-turbo",
    "question_generator": "gpt-3.5-turbo",
    "streaming": "gpt-3.5-turbo",
    "embedding": "text-embedding-ada-002"  # embeddingモデルは変更不可
}
```

例：高精度版を使いたい場合

```python
GPT_MODELS = {
    "main": "gpt-4-turbo-preview",
    "classifier": "gpt-4",
    "question_generator": "gpt-4",
    "streaming": "gpt-4-turbo-preview",
    "embedding": "text-embedding-3-large"  # より高精度なembedding
}
```

## Temperature設定

創造性のパラメータも同様に調整可能です：

```python
TEMPERATURE_SETTINGS = {
    "main": 0,              # 0 = 決定的（同じ入力に対して同じ出力）
    "classifier": 0,        # 分類は確実性重視
    "question_generator": 0.2,  # 少し柔軟性を持たせる
    "streaming": 0         # 正確性重視
}
```

## 対応ファイル一覧

以下のファイルが`config.py`の設定を使用しています：

- `src/chat.py` - チャット応答と深掘り質問
- `src/predict_crime_type.py` - 罪名予測
- `src/embedding.py` - RAG用のembedding生成

## 利用可能なモデル（2024年時点）

### GPTモデル
- `gpt-4o` - マルチモーダル対応で高精度
- `gpt-4o-mini` - コストと速度重視の軽量版
- `gpt-4` - 従来の高精度モデル
- `gpt-3.5-turbo` - 高速・低コスト
- `gpt-3.5-turbo-1106` - 改良版のGPT-3.5

### Embeddingモデル
- `text-embedding-ada-002` - 標準的なembedding
- `text-embedding-3-small` - 小型・高速
- `text-embedding-3-large` - 大型・高精度

## 注意事項

1. **コスト**: GPT-4はGPT-3.5より約10倍高額です
2. **速度**: GPT-3.5はGPT-4より約2-3倍高速です
3. **精度**: 法律相談の精度を重視する場合はGPT-4推奨
4. **API制限**: モデルによってレート制限が異なります
