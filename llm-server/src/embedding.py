import openai
from openai import OpenAI
import numpy as np
from typing import List, Union
import src.config as config

def ada(text: str) -> List[float]:
    """
    OpenAI APIを使用してテキストをembeddingに変換
    設定ファイルで指定されたembeddingモデルを使用
    """
    client = OpenAI()
    response = client.embeddings.create(
        model=config.get_model("embedding"),
        input=text
    )
    return response.data[0].embedding

def ada_batch(texts: List[str]) -> List[List[float]]:
    """
    複数のテキストを一度にembeddingに変換
    """
    client = OpenAI()
    response = client.embeddings.create(
        model=config.get_model("embedding"),
        input=texts
    )
    return [data.embedding for data in response.data]

def cosine_similarity(vec1: Union[List[float], np.ndarray], 
                     vec2: Union[List[float], np.ndarray]) -> float:
    """
    2つのベクトル間のコサイン類似度を計算
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))