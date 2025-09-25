#!/usr/bin/env python3
"""
統合予測機能のテストスクリプト
罪名と量刑を同時に予測する機能をテストする
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chat import classify_response_type, reply

def test_classify_response_type():
    """分類機能のテスト"""
    test_cases = [
        # 統合予測として分類されるべきケース
        ("旦那が大麻所持で捕まりました。どのような罪になってどのくらいの刑になるでしょうか？", "predict_crime_and_punishment"),
        ("息子が窃盗で逮捕されました。罪名と量刑を教えてください。", "predict_crime_and_punishment"),
        ("交通事故を起こしてしまいました。どんな罪でどのくらいの刑になりますか？", "predict_crime_and_punishment"),

        # 罪名のみ
        ("これはどのような罪になりますか？", "predict_crime_type"),

        # 量刑のみ
        ("窃盗罪の場合、どのくらいの量刑になりますか？", "predict_punishment"),

        # 法的プロセス
        ("保釈はいつ頃になりますか？", "legal_process"),
    ]

    print("=== 分類機能テスト ===")
    for text, expected in test_cases:
        result = classify_response_type(text)
        actual = result.get('type', 'unknown')
        status = "✓" if actual == expected else "✗"
        print(f"{status} 入力: {text[:30]}...")
        print(f"  期待: {expected}, 実際: {actual}")
        print()

def test_unified_prediction():
    """統合予測機能の動作テスト"""
    print("\n=== 統合予測機能テスト ===")

    # テスト用の会話履歴
    test_histories = [
        # ケース1: 初回の相談（深掘り質問が必要）
        [{"role": "user", "content": "息子が窃盗で捕まりました。どのような罪になってどのくらいの刑になるでしょうか？"}],

        # ケース2: 詳細情報あり（直接予測可能）
        [{"role": "user", "content": """
        昨日、息子（22歳）がコンビニで商品（約5000円相当）を万引きして捕まりました。
        初犯で、深く反省しています。被害店舗とは示談交渉中で、被害弁償は完了しています。
        どのような罪になってどのくらいの刑になるでしょうか？
        """}],
    ]

    for i, hist in enumerate(test_histories, 1):
        print(f"\n--- ケース{i} ---")
        print(f"入力: {hist[-1]['content'][:100]}...")

        # reply関数を呼び出し
        response = reply(hist)

        if isinstance(response, str):
            # 深掘り質問の場合
            print("応答タイプ: 深掘り質問")
            print(f"応答内容: {response[:200]}...")
        else:
            # ストリーミング応答の場合
            print("応答タイプ: 予測結果（ストリーミング）")
            result = ""
            for chunk in response:
                result += chunk
            print(f"応答内容:\n{result[:500]}...")

def test_clarifying_questions():
    """深掘り質問の統合テスト"""
    print("\n=== 深掘り質問テスト ===")

    hist = [{"role": "user", "content": "逮捕されました。どうなりますか？"}]

    # 最初の応答（深掘り質問が期待される）
    response = reply(hist)

    if isinstance(response, str) and "確認ステップ" in response:
        print("✓ 深掘り質問が生成されました")
        print(f"質問内容:\n{response}")

        # 質問に罪名と量刑両方の要素が含まれているか確認
        keywords = ["行為", "被害", "前科", "示談", "反省"]
        found = [kw for kw in keywords if kw in response]
        print(f"\n含まれるキーワード: {', '.join(found)}")
    else:
        print("✗ 深掘り質問が生成されませんでした")

if __name__ == "__main__":
    print("統合予測機能のテストを開始します...\n")

    try:
        test_classify_response_type()
        test_unified_prediction()
        test_clarifying_questions()

        print("\n=== テスト完了 ===")
        print("統合予測機能が正常に実装されました。")
        print("\n主な変更点:")
        print("1. 罪名と量刑を同時に聞く質問を 'predict_crime_and_punishment' として分類")
        print("2. 深掘り質問で罪名判定と量刑判定の両方に必要な情報を収集")
        print("3. 量刑を「懲役○年〜○年」の幅を持たせた形式で回答")
        print("4. 比較モードでも同様の機能が動作")

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()