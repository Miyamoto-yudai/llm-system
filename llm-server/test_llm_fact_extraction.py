#!/usr/bin/env python3
"""LLMベースの事実抽出機能のテストスクリプト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chat import clarification_manager

def test_negative_expressions():
    """否定表現の正しい理解をテスト"""
    print("\n=== テスト1: 否定表現の理解 ===")

    # テストケース：「前科はありません」
    hist = [
        {"role": "user", "content": "相手の右手首を骨折させちゃいました。わざとです。昨日の夜、駅のホームで友人を殴りました。前科はありません。示談はありません、昨日のことなので。"}
    ]

    response_type_value = 'predict_crime_and_punishment'
    facts = clarification_manager._extract_known_facts(hist, response_type_value)

    print("抽出された情報:")
    for fact in facts:
        print(f"  {fact}")

    # 検証
    has_correct_criminal_record = any("前科：なし" in fact or "前科：ない" in fact for fact in facts)
    has_correct_settlement = any("示談：なし" in fact or "示談：ない" in fact or "示談：未成立" in fact for fact in facts)

    if has_correct_criminal_record:
        print("✓ 前科なしを正しく認識")
    else:
        print("✗ 前科の判定が誤っています")

    if has_correct_settlement:
        print("✓ 示談なしを正しく認識")
    else:
        print("✗ 示談の判定が誤っています")

def test_complex_case():
    """複雑なケースでの情報抽出テスト"""
    print("\n=== テスト2: 複雑な情報の抽出 ===")

    hist = [
        {"role": "user", "content": "交通事故を起こしました。信号無視の歩行者を轢いてしまい、相手は軽傷です。"},
        {"role": "assistant", "content": "詳細を教えてください"},
        {"role": "user", "content": "初犯です。被害者とは示談交渉中で、10万円で話がまとまりそうです。深く反省しています。"}
    ]

    response_type_value = 'predict_crime_and_punishment'
    facts = clarification_manager._extract_known_facts(hist, response_type_value)

    print("抽出された情報:")
    for fact in facts:
        print(f"  {fact}")

    # 期待される情報が含まれているか確認
    expected_items = {
        "行為": False,
        "被害": False,
        "前科": False,
        "示談": False,
        "反省": False
    }

    for fact in facts:
        for key in expected_items.keys():
            if key in fact:
                expected_items[key] = True

    print("\n情報の網羅性:")
    for key, found in expected_items.items():
        status = "✓" if found else "✗"
        print(f"  {status} {key}")

def test_minimal_info():
    """最小限の情報での動作テスト"""
    print("\n=== テスト3: 最小限の情報 ===")

    hist = [
        {"role": "user", "content": "暴行事件を起こしました"}
    ]

    response_type_value = 'predict_crime_type'
    facts = clarification_manager._extract_known_facts(hist, response_type_value)

    print("抽出された情報:")
    for fact in facts:
        print(f"  {fact}")

    if facts and facts[0] != "相談内容を確認中":
        print("✓ 最小限の情報でも動作")
    else:
        print("✓ 情報不足を適切に処理")

def test_conciseness():
    """簡潔性のテスト"""
    print("\n=== テスト4: 簡潔性の確認 ===")

    hist = [
        {"role": "user", "content": "昨日の午後3時頃、渋谷の交差点で信号無視をしてしまい、横断歩道を渡っていた70歳くらいの高齢者の方を車で轢いてしまいました。相手の方は足を骨折して全治3ヶ月の重傷です。私は飲酒はしていませんでした。"}
    ]

    response_type_value = 'predict_crime_type'
    facts = clarification_manager._extract_known_facts(hist, response_type_value)

    print("抽出された情報:")
    all_concise = True
    for fact in facts:
        print(f"  {fact}")
        # 各項目が簡潔か確認（目安：20文字以内）
        if "：" in fact:
            content = fact.split("：", 1)[1]
            if len(content) > 20:
                all_concise = False
                print(f"    ⚠ 長い: {len(content)}文字")

    if all_concise:
        print("✓ 全ての項目が簡潔")
    else:
        print("✗ 一部の項目が長すぎます")

if __name__ == "__main__":
    print("LLMベース事実抽出テスト")
    print("=" * 50)

    test_negative_expressions()
    test_complex_case()
    test_minimal_info()
    test_conciseness()

    print("\n" + "=" * 50)
    print("テスト完了")