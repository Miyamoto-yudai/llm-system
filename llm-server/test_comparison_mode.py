#!/usr/bin/env python3
"""
比較モードのテストスクリプト
データあり（通常モード）とデータなし（LLMのみ）の応答を比較テスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import src.chat as chat_with_data
import src.chat_comparison as chat_without_data


def test_comparison():
    """同じ入力に対して両方のモードで応答を生成して比較"""

    test_cases = [
        # ケース1: シンプルな罪名予測
        [{"role": "user", "content": "友人から借りたものを売ってしまいました。どんな罪になりますか？"}],

        # ケース2: 詳細が不足している量刑予測
        [{"role": "user", "content": "窃盗で捕まりました。どのくらいの刑になりますか？"}],

        # ケース3: 法プロセスの質問
        [{"role": "user", "content": "逮捕されてから起訴されるまでの流れを教えてください。"}]
    ]

    for i, hist in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"テストケース {i}: {hist[0]['content']}")
        print('='*60)

        # データありモード
        print("\n【データありモード（通常）】")
        print("-" * 30)
        response_with_data = chat_with_data.reply(hist)
        if isinstance(response_with_data, str):
            print(response_with_data)
        else:
            full_response = ""
            for chunk in response_with_data:
                full_response += chunk
            print(full_response)

        # データなしモード
        print("\n【LLMのみモード】")
        print("-" * 30)
        response_without_data = chat_without_data.reply_without_data(hist)
        if isinstance(response_without_data, str):
            print(response_without_data)
        else:
            full_response = ""
            for chunk in response_without_data:
                full_response += chunk
            print(full_response)

        print("\n" + "="*60)
        input("次のテストケースに進むにはEnterキーを押してください...")


def test_clarification_rounds():
    """深掘り質問のラウンド数を比較"""

    print("\n" + "="*60)
    print("深掘り質問のラウンド数比較テスト")
    print("="*60)

    # 初期の曖昧な質問
    hist = [{"role": "user", "content": "犯罪を犯してしまいました。どうすればいいですか？"}]

    # データありモード
    print("\n【データありモード】")
    rounds_with_data = 0
    current_hist = hist.copy()

    for round_num in range(5):  # 最大5ラウンド
        response = chat_with_data.reply(current_hist)
        if isinstance(response, str):
            response_text = response
        else:
            response_text = "".join(response)

        if "【確認ステップ" in response_text:
            rounds_with_data += 1
            print(f"ラウンド {rounds_with_data}: 深掘り質問を検出")
            print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
            # ダミーの回答を追加
            current_hist.append({"role": "assistant", "content": response_text})
            current_hist.append({"role": "user", "content": "窃盗です。コンビニで商品を盗みました。"})
        else:
            print(f"最終応答（{rounds_with_data}回の深掘り後）")
            break

    # データなしモード
    print("\n【LLMのみモード】")
    rounds_without_data = 0
    current_hist = hist.copy()

    for round_num in range(5):  # 最大5ラウンド
        response = chat_without_data.reply_without_data(current_hist)
        if isinstance(response, str):
            response_text = response
        else:
            response_text = "".join(response)

        if "【確認ステップ" in response_text:
            rounds_without_data += 1
            print(f"ラウンド {rounds_without_data}: 深掘り質問を検出")
            print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
            # ダミーの回答を追加
            current_hist.append({"role": "assistant", "content": response_text})
            current_hist.append({"role": "user", "content": "窃盗です。コンビニで商品を盗みました。"})
        else:
            print(f"最終応答（{rounds_without_data}回の深掘り後）")
            break

    print("\n" + "="*60)
    print(f"結果: データあり={rounds_with_data}回, LLMのみ={rounds_without_data}回")
    print("="*60)


if __name__ == "__main__":
    print("比較モードテスト開始")
    print("注意: このテストはOpenAI APIを使用します")

    choice = input("\n実行するテストを選択してください:\n1. 基本比較テスト\n2. 深掘り質問ラウンド数比較\n3. 両方\n選択 (1/2/3): ")

    if choice == "1":
        test_comparison()
    elif choice == "2":
        test_clarification_rounds()
    elif choice == "3":
        test_comparison()
        test_clarification_rounds()
    else:
        print("無効な選択です")

    print("\nテスト完了")