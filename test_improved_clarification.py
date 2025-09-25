#!/usr/bin/env python3
"""深掘り質問改善のテストスクリプト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chat import clarification_manager, reply

def test_early_termination():
    """2-3ラウンドで自然に終了するかテスト"""
    print("\n=== テスト1: 早期終了の確認 ===")

    # 罪名予測：基本3要素が揃った場合
    hist = [
        {"role": "user", "content": "交通事故を起こしました"},
        {"role": "assistant", "content": "【確認ステップ 第1回】\n詳細を教えてください"},
        {"role": "user", "content": "昨日の午後3時頃、交差点で信号無視の歩行者を轢いてしまいました。相手は足を骨折し、すぐに救急車を呼びました。私は飲酒していません。"}
    ]

    response_type = {"type": "predict_crime_type"}
    result = clarification_manager.should_ask_more(hist, response_type)

    if result:
        print(f"2回目の質問:\n{result}\n")
        # 2回目の回答
        hist.append({"role": "assistant", "content": result})
        hist.append({"role": "user", "content": "免許は持っています。初犯です。警察には連絡済みです。"})

        # 3回目のチェック（ここで終了すべき）
        result = clarification_manager.should_ask_more(hist, response_type)
        if result:
            print(f"3回目の質問:\n{result}\n")
        else:
            print("✓ 2ラウンドで正常に終了しました")
    else:
        print("✓ 1ラウンドで終了しました")

def test_unknown_response_handling():
    """「わからない」回答への対応テスト"""
    print("\n=== テスト2: 「わからない」回答の処理 ===")

    hist = [
        {"role": "user", "content": "暴行事件を起こしました"},
        {"role": "assistant", "content": "【確認ステップ 第1回】\n【現在判明している情報】\n・相談内容を伺っています\n\n状況を把握するため、次の点を教えてください。\n1. いつ・どこで起きた出来事でしょうか？\n2. 被害者や関係者は誰ですか？\n3. 具体的にどのような暴行を行いましたか？"},
        {"role": "user", "content": "いつかは覚えていません。相手は知らない人です。殴りました。"}
    ]

    response_type = {"type": "predict_crime_type"}
    result = clarification_manager.should_ask_more(hist, response_type)

    if result:
        print(f"次の質問（「わからない」項目は再質問しない）:\n{result}\n")
        # 「いつ」に関する質問が除外されているか確認
        if "いつ" not in result and "時期" not in result:
            print("✓ 「わからない」項目の再質問を回避しました")
        else:
            print("✗ 「わからない」項目を再度質問しています")
    else:
        print("質問終了")

def test_facts_summary():
    """現在判明している情報の表示テスト"""
    print("\n=== テスト3: 現在判明している情報の表示 ===")

    hist = [
        {"role": "user", "content": "窃盗で捕まりました。コンビニで1万円相当の商品を盗みました。"},
        {"role": "assistant", "content": "【確認ステップ 第1回】\n質問..."},
        {"role": "user", "content": "前科はありません。被害者との示談はまだです。反省しています。"}
    ]

    response_type = {"type": "predict_crime_and_punishment"}
    result = clarification_manager.should_ask_more(hist, response_type)

    if result and "【現在判明している情報】" in result:
        print("✓ 現在判明している情報が表示されています:")
        lines = result.split('\n')
        for line in lines:
            if line.startswith('・'):
                print(f"  {line}")
    else:
        print("✗ 現在判明している情報が表示されていません")

def test_rounds_limit():
    """3ラウンド以内で終了するかテスト"""
    print("\n=== テスト4: 3ラウンド以内での終了確認 ===")

    hist = [
        {"role": "user", "content": "事件を起こしました"}
    ]

    response_type = {"type": "predict_crime_and_punishment"}
    round_count = 0

    while True:
        result = clarification_manager.should_ask_more(hist, response_type)
        if not result:
            break

        round_count += 1
        print(f"ラウンド {round_count}:")

        # 質問を追加
        hist.append({"role": "assistant", "content": result})

        # 最小限の回答を追加
        if round_count == 1:
            hist.append({"role": "user", "content": "暴行事件です。相手を殴りました。"})
        elif round_count == 2:
            hist.append({"role": "user", "content": "怪我は軽傷です。前科なし。示談はまだです。"})
        elif round_count == 3:
            hist.append({"role": "user", "content": "計画性はありません。反省しています。"})
        else:
            hist.append({"role": "user", "content": "その他の情報です。"})

    print(f"\n終了ラウンド数: {round_count}")
    if round_count <= 3:
        print("✓ 3ラウンド以内で終了しました")
    else:
        print(f"✗ {round_count}ラウンドかかりました（3ラウンドを超過）")

if __name__ == "__main__":
    print("深掘り質問改善テスト")
    print("=" * 50)

    test_early_termination()
    test_unknown_response_handling()
    test_facts_summary()
    test_rounds_limit()

    print("\n" + "=" * 50)
    print("テスト完了")