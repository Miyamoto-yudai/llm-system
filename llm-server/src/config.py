"""
OpenAI GPTモデルの統一設定ファイル
全てのモデル指定をここで一元管理します
"""

# GPTモデルの設定
GPT_MODELS = {
    # メインモデル（高精度が必要な処理用）
    "main": "gpt-4.1",
    
    # 分類用モデル（応答タイプの判定等）
    "classifier": "gpt-4.1",
    
    # 質問生成用モデル（深掘り質問の生成等）
    "question_generator": "gpt-5",
    
    # ストリーミング対応モデル（リアルタイム応答用）
    "streaming": "gpt-4.1",
    
    # Embedding用モデル
    "embedding": "text-embedding-ada-002"
}

# Temperature設定（モデルごとの創造性パラメータ）
TEMPERATURE_SETTINGS = {
    "main": 0,              # 正確性重視
    "classifier": 0,        # 確実な分類
    "question_generator": 0.2,  # 少し柔軟性を持たせる
    "streaming": 0         # 正確性重視
}

# その他の設定
SETTINGS = {
    "max_tokens": None,  # Noneの場合はデフォルト
    "stream_enabled": True,  # ストリーミングを有効化
    "response_format_json": {"type": "json_object"}  # JSON出力形式
}

def get_model(purpose="main"):
    """
    用途に応じたモデル名を取得
    
    Args:
        purpose (str): 用途を指定
            - "main": メインの処理用
            - "classifier": 分類用
            - "question_generator": 質問生成用
            - "streaming": ストリーミング用
            - "embedding": Embedding用
    
    Returns:
        str: モデル名
    """
    return GPT_MODELS.get(purpose, GPT_MODELS["main"])

def get_temperature(purpose="main"):
    """
    用途に応じたtemperatureを取得
    
    Args:
        purpose (str): 用途を指定
    
    Returns:
        float: temperature値
    """
    return TEMPERATURE_SETTINGS.get(purpose, 0)