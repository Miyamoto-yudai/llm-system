#!/usr/bin/env python3
"""
任意追加質問機能のテストスクリプト
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import src.chat as chat


def test_optional_questions():
    """任意追加質問が正しく生成されるかテスト"""
    print("=" * 60)
    print("任意追加質問機能のテスト")
    print("=" * 60)

    # テストケース1: 罪名と量刑の統合予測（詳細情報を含む）
    print("\n【テスト1: 罪名と量刑の統合予測】")
    hist1 = [
        {"role": "user", "content": "昨日、酒を飲んで車を運転し、信号無視をして歩行者を轢いてしまいました。被害者は骨折で全治3ヶ月です。呼気中アルコール濃度は0.3mgでした。初犯で前科はありません。示談は成立しておらず、被害者は厳罰を望んでいます。事故後すぐに救護措置を取り、警察にも通報しました。深く反省しており、今後は一切飲酒運転をしないと誓います。"},
    ]

    # 深掘り質問をスキップするために十分な情報を含む
    response = chat.reply(hist1)
    full_response = ""
    if isinstance(response, str):
        print("\n回答:")
        print(response)
        full_response = response
    else:
        print("\n回答:")
        for chunk in response:
            full_response += chunk
        print(full_response)

    # 任意追加質問が含まれているか確認
    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        print("\n✅ 任意追加質問が正しく生成されました")
    else:
        print("\n❌ 任意追加質問が生成されませんでした")

    print("\n" + "=" * 60)

    # テストケース2: 追加質問への回答による詳細分析
    print("\n【テスト2: 追加質問への回答】")
    hist2 = hist1 + [
        {"role": "assistant", "content": full_response},
        {"role": "user", "content": "1. 示談は成立していません\n2. 被害者は厳罰を望んでいます\n3. 飲酒量はビール500ml程度でした"}
    ]

    response2 = chat.reply(hist2)
    if isinstance(response2, str):
        print("\n詳細分析:")
        print(response2)
    else:
        print("\n詳細分析:")
        full_response2 = ""
        for chunk in response2:
            full_response2 += chunk
        print(full_response2)

    # 2回目には任意追加質問が含まれないことを確認
    if chat.OPTIONAL_FOLLOW_UP_PREFIX not in full_response2:
        print("\n✅ 詳細分析では任意追加質問が含まれていません（正常）")
    else:
        print("\n❌ 詳細分析にも任意追加質問が含まれています（異常）")

    print("\n" + "=" * 60)

    # テストケース3: 新規相談の判定
    print("\n【テスト3: 新規相談の判定】")
    hist3 = hist2 + [
        {"role": "assistant", "content": full_response2},
        {"role": "user", "content": "別の相談ですが、友人が大麻を所持していて逮捕されました。"}
    ]

    continuation = chat.detect_continuation_intent(hist3)
    print(f"判定結果: {continuation}")

    if continuation == "new_consultation":
        print("✅ 新規相談として正しく判定されました")
    else:
        print("❌ 継続として誤判定されました")


def test_continuation_detection():
    """継続判定ロジックのテスト"""
    print("\n" + "=" * 60)
    print("継続判定ロジックのテスト")
    print("=" * 60)

    test_cases = [
        {
            "name": "任意質問への番号付き回答",
            "hist": [
                {"role": "assistant", "content": f"{chat.OPTIONAL_FOLLOW_UP_PREFIX}\n1. 前科はありますか？\n2. 示談の状況は？"},
                {"role": "user", "content": "1. 前科はありません\n2. 示談交渉中です"}
            ],
            "expected": "continuation"
        },
        {
            "name": "新規相談キーワード",
            "hist": [
                {"role": "assistant", "content": "量刑は懲役3年執行猶予5年が見込まれます"},
                {"role": "user", "content": "別の質問ですが、離婚について相談したいです"}
            ],
            "expected": "new_consultation"
        },
        {
            "name": "追加情報の提供",
            "hist": [
                {"role": "assistant", "content": f"{chat.OPTIONAL_FOLLOW_UP_PREFIX}\n詳細を教えてください"},
                {"role": "user", "content": "その件について、実は共犯者がいました"}
            ],
            "expected": "continuation"
        }
    ]

    for test in test_cases:
        print(f"\nテスト: {test['name']}")
        result = chat.detect_continuation_intent(test['hist'])
        if result == test['expected']:
            print(f"✅ 期待通り: {result}")
        else:
            print(f"❌ 期待: {test['expected']}, 実際: {result}")


if __name__ == "__main__":
    print("任意追加質問機能のテストを開始します...\n")

    try:
        test_optional_questions()
        test_continuation_detection()
        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()