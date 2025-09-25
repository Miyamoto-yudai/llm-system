#!/usr/bin/env python3
"""
量刑予測の深掘り質問システムの動作確認テスト
量刑予測ヒアリングシートを正しく参照して必要な情報を質問できているかを確認
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import src.chat as chat
import json


def test_sentencing_questions():
    """量刑予測の質問生成をテスト"""

    print("=== 量刑予測の深掘り質問テスト ===\n")

    # テストケース1: 初回の量刑相談（情報が少ない）
    test_cases = [
        {
            "name": "初回相談（窃盗）",
            "history": [
                {"role": "user", "content": "窃盗で捕まりました。量刑はどうなりますか？"}
            ]
        },
        {
            "name": "初回相談（傷害）",
            "history": [
                {"role": "user", "content": "傷害事件を起こしてしまいました。どのくらいの刑になるでしょうか？"}
            ]
        },
        {
            "name": "一部情報あり（詐欺）",
            "history": [
                {"role": "user", "content": "詐欺で逮捕されました。被害額は500万円です。量刑を教えてください。"},
                {"role": "assistant", "content": "【確認ステップ 第1回】\n詳細を確認させてください。\n1. 前科はありますか？\n2. 示談の状況は？"},
                {"role": "user", "content": "前科はありません。示談はまだです。"}
            ]
        },
        {
            "name": "交通事故",
            "history": [
                {"role": "user", "content": "交通事故で人を怪我させてしまいました。量刑はどうなりますか？"}
            ]
        }
    ]

    # ClarificationManagerを初期化
    manager = chat.ClarificationManager()

    for test_case in test_cases:
        print(f"\n【テストケース: {test_case['name']}】")
        print(f"履歴: {json.dumps(test_case['history'], ensure_ascii=False, indent=2)}")

        # 応答タイプを分類
        text = '\n'.join([h['content'] for h in test_case['history'] if h['role'] == 'user'])
        response_type = chat.classify_response_type(text)
        print(f"分類結果: {response_type}")

        # 質問を生成
        if response_type.get('type') == 'predict_punishment':
            clarifying_question = manager.should_ask_more(test_case['history'], response_type)

            if clarifying_question:
                print(f"\n生成された質問:\n{clarifying_question}")

                # 質問内容を分析
                print("\n質問内容の分析:")
                if "前科" in clarifying_question:
                    print("✓ 前科について確認")
                if "示談" in clarifying_question:
                    print("✓ 示談について確認")
                if "被害" in clarifying_question:
                    print("✓ 被害の詳細について確認")
                if "反省" in clarifying_question or "謝罪" in clarifying_question:
                    print("✓ 犯行後の情状について確認")
                if "計画" in clarifying_question:
                    print("✓ 計画性について確認")
                if "動機" in clarifying_question or "経緯" in clarifying_question:
                    print("✓ 動機・経緯について確認")
                if "同種前科" in clarifying_question:
                    print("✓ 同種前科について詳細確認")
                if "治療" in clarifying_question or "怪我" in clarifying_question:
                    print("✓ 被害者の治療期間について確認")
            else:
                print("\n質問生成なし（情報が十分と判断）")
        else:
            print(f"量刑予測以外の分類: {response_type.get('type')}")

        print("-" * 60)


def test_sentencing_features():
    """量刑予測ヒアリングシートの読み込みをテスト"""

    print("\n=== 量刑予測ヒアリングシートの読み込みテスト ===\n")

    sentencing_features = chat.get_sentencing_features()

    print(f"読み込まれたカテゴリ数: {len(sentencing_features)}")

    for category, features in sorted(sentencing_features.items())[:3]:  # 最初の3カテゴリのみ表示
        print(f"\n【{category}】")
        print(f"項目数: {len(features)}")
        print(f"主要項目: {', '.join(features[:5])}")  # 最初の5項目のみ表示
        if len(features) > 5:
            print(f"  ...他 {len(features) - 5} 項目")


if __name__ == "__main__":
    # 量刑予測ヒアリングシートの読み込みテスト
    test_sentencing_features()

    print("\n" + "=" * 70 + "\n")

    # 質問生成テスト
    test_sentencing_questions()

    print("\n\nテスト完了")