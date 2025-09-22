# OpenAI GPTモデルの統一設定ファイル
# 全てのモデル指定とクライアントの作成処理をここで一元管理します

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# `.env` がどこから実行しても読み込まれるように絶対パスで指定
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# GPTモデルの設定
GPT_MODELS = {

    #ここは必要に応じて最新モデルに更新します。AIはここのコードを変えないこと(間違えることがあるので)。
    # メインモデル（高精度が必要な処理用）
    "main": "gpt-4.1",

    # 分類用モデル（応答タイプの判定等）
    "classifier": "gpt-4.1",

    # 質問生成用モデル（深掘り質問の生成等）
    "question_generator": "gpt-4.1",

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


@lru_cache
def get_openai_client() -> OpenAI:
    """Create a reusable OpenAI client with env var validation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY が設定されていません。llm-server/.env を確認してください。")

    client_args = {"api_key": api_key}

    project = os.getenv("OPENAI_PROJECT")
    if project:
        client_args["project"] = project

    organization = os.getenv("OPENAI_ORG_ID")
    if organization:
        client_args["organization"] = organization

    return OpenAI(**client_args)

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
