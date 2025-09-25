#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深掘り質問機能のテストスクリプト
RAGが利用できない場合はフォールバック処理を使用
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# OpenAI APIキーを設定（環境変数から取得）
if not os.getenv('OPENAI_API_KEY'):
    print("Warning: OPENAI_API_KEY is not set. RAG features will be disabled.")
    print("To enable RAG, set the environment variable: export OPENAI_API_KEY='your-api-key'")
    print("Continuing with fallback mode...\n")

from src.chat import reply, classify_response_type, generate_clarifying_question, generate_clarifying_question_fallback

def test_clarifying_questions():
    """
    深掘り質問機能のテスト
    """
    print("=" * 60)
    print("深掘り質問機能のテスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "交通事故（罪名予測）",
            "message": "自動車事故です、どのような罪にとわれるでしょうか？",
            "expected_type": "predict_crime_type"
        },
        {
            "name": "大麻所持（量刑予測）",
            "message": "旦那が大麻所持の疑いで捕まりました、量刑はどうなるでしょうか？",
            "expected_type": "predict_punishment"
        },
        {
            "name": "保釈（法プロセス）",
            "message": "旦那が大麻所持の疑いで捕まりました、いつ頃に保釈されるでしょうか？",
            "expected_type": "legal_process"
        },
        {
            "name": "窃盗（罪名予測）",
            "message": "店で商品を間違えて持ち出してしまいました。どのような罪になりますか？",
            "expected_type": "predict_crime_type"
        },
        {
            "name": "暴行事件（量刑予測）",
            "message": "酔って人を殴ってしまいました。刑はどのくらい重くなりますか？",
            "expected_type": "predict_punishment"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n【テストケース {i}: {test_case['name']}】")
        print(f"相談内容: {test_case['message']}")
        print("-" * 40)
        
        # 相談タイプの分類
        response_type = classify_response_type(test_case['message'])
        print(f"判定された相談タイプ: {response_type['type']}")
        
        if response_type['type'] != test_case['expected_type']:
            print(f"⚠️ 期待値と異なります（期待: {test_case['expected_type']}）")
        
        # 深掘り質問の生成
        if response_type['type'] in ['predict_crime_type', 'predict_punishment', 'legal_process']:
            hist = [{"role": "user", "content": test_case['message']}]
            
            try:
                # RAG対応版を試す
                questions = generate_clarifying_question(hist, response_type)
                print("\n生成された深掘り質問（RAG版）:")
            except Exception as e:
                # フォールバック処理
                print(f"RAG処理でエラー: {e}")
                questions = generate_clarifying_question_fallback(hist, response_type)
                print("\n生成された深掘り質問（フォールバック版）:")
            
            print(questions)
        else:
            print(f"相談タイプ '{response_type['type']}' は深掘り質問の対象外です")
        
        print("=" * 60)

def test_full_conversation():
    """
    完全な会話フローのテスト（最初の応答で深掘り質問が出ることを確認）
    """
    print("\n" + "=" * 60)
    print("完全な会話フローのテスト")
    print("=" * 60)
    
    # 初回の相談
    hist1 = [{"role": "user", "content": "自動車事故です、どのような罪にとわれるでしょうか？"}]
    
    print("\n【初回の相談】")
    print(f"ユーザー: {hist1[0]['content']}")
    print("\nアシスタントの応答:")
    
    # replyの結果をストリーミングで受け取る場合の処理
    response = reply(hist1)
    if hasattr(response, '__iter__') and not isinstance(response, str):
        # ジェネレータの場合
        response_text = ''.join(response)
    else:
        response_text = response
    
    print(response_text)
    
    # 2回目の応答（深掘り質問への回答後）
    hist2 = [
        {"role": "user", "content": "自動車事故です、どのような罪にとわれるでしょうか？"},
        {"role": "assistant", "content": response_text},
        {"role": "user", "content": "車同士で交差点です。相手にけがはありません。"}
    ]
    
    print("\n【深掘り質問への回答後】")
    print(f"ユーザー: {hist2[-1]['content']}")
    print("\nアシスタントの応答:")
    
    response2 = reply(hist2)
    if hasattr(response2, '__iter__') and not isinstance(response2, str):
        response_text2 = ''.join(response2)
    else:
        response_text2 = response2
    
    print(response_text2)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("\n深掘り質問機能改善のテスト開始\n")
    
    # 基本的な深掘り質問のテスト
    test_clarifying_questions()
    
    # 完全な会話フローのテスト
    print("\n\n続いて、完全な会話フローをテストします...")
    test_full_conversation()
    
    print("\n\nテスト完了！")
    print("\n補足:")
    print("- RAGデータが生成されていない場合、フォールバック処理が使用されます")
    print("- RAGデータを生成するには、OPENAI_API_KEYを設定して以下を実行してください:")
    print("  export OPENAI_API_KEY='your-api-key'")
    print("  python -m src.rag_loader")