#!/usr/bin/env python3
"""
ユーザー報告のケースを再現するテストスクリプト
深掘り質問後の本回答に任意質問が付与されるかを確認
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import src.chat as chat


def test_user_case():
    """ユーザーが報告したケースを再現"""
    print("=" * 60)
    print("ユーザー報告ケースのテスト")
    print("深掘り質問 → ユーザー回答 → 本回答のフロー")
    print("=" * 60)

    # 初回の相談（情報不足で深掘り質問が発生する）
    hist1 = [
        {"role": "user", "content": "友人と喧嘩して殴ってしまいました。相手は怪我をしています。"}
    ]

    print("\n【ステップ1: 初回相談】")
    print("ユーザー:", hist1[0]["content"])

    response1 = chat.reply(hist1)
    if isinstance(response1, str):
        clarifying_question = response1
    else:
        clarifying_question = ''.join(response1)

    print("\nボット（深掘り質問）:")
    print(clarifying_question)

    # 深掘り質問への回答
    hist2 = hist1 + [
        {"role": "assistant", "content": clarifying_question},
        {"role": "user", "content": "まだ診断結果とかはわからないです。素手です。腕を殴りました。謝罪はしました。相手の右手首の骨にヒビが入ったようです"}
    ]

    print("\n【ステップ2: 深掘り質問への回答】")
    print("ユーザー:", hist2[-1]["content"])

    # 本回答の生成（ここで任意質問が付与されるべき）
    print("\n【ステップ3: 本回答生成】")
    response2 = chat.reply(hist2)

    full_response = ""
    if isinstance(response2, str):
        full_response = response2
    else:
        for chunk in response2:
            full_response += chunk

    print("\nボット（本回答）:")
    print(full_response)

    # 検証
    print("\n" + "=" * 60)
    print("【検証結果】")

    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        print("✅ 任意追加質問が正しく生成されました！")

        # 任意質問部分を抽出して表示
        optional_part = full_response.split(chat.OPTIONAL_FOLLOW_UP_PREFIX)[1]
        print("\n生成された任意質問:")
        print(chat.OPTIONAL_FOLLOW_UP_PREFIX + optional_part[:200] + "...")
    else:
        print("❌ 任意追加質問が生成されませんでした（バグ）")
        print("\n回答の最後の部分:")
        print(full_response[-300:])


def test_clarification_flow():
    """深掘り質問フローの各段階で任意質問の判定をテスト"""
    print("\n" + "=" * 60)
    print("深掘り質問フローの判定テスト")
    print("=" * 60)

    manager = chat.optional_follow_up_manager

    # ケース1: 深掘り質問直後（任意質問なし）
    hist_clarifying = [
        {"role": "user", "content": "相談内容"},
        {"role": "assistant", "content": f"{chat.CLARIFY_PREFIX} 第1回】\n詳細を教えてください"}
    ]

    result1 = manager.should_add_optional_questions(hist_clarifying, {"type": "predict_crime_and_punishment"})
    print(f"\n深掘り質問直後: {result1} (期待値: False)")

    # ケース2: ユーザーが深掘り質問に回答後（任意質問あり）
    hist_after_answer = [
        {"role": "user", "content": "相談内容"},
        {"role": "assistant", "content": f"{chat.CLARIFY_PREFIX} 第1回】\n詳細を教えてください"},
        {"role": "user", "content": "詳細情報です"}
    ]

    result2 = manager.should_add_optional_questions(hist_after_answer, {"type": "predict_crime_and_punishment"})
    print(f"ユーザー回答後: {result2} (期待値: True)")

    # ケース3: 既に任意質問済み（任意質問なし）
    hist_already_optional = [
        {"role": "user", "content": "相談内容"},
        {"role": "assistant", "content": f"回答内容\n{chat.OPTIONAL_FOLLOW_UP_PREFIX}\n任意質問"},
        {"role": "user", "content": "追加情報"}
    ]

    result3 = manager.should_add_optional_questions(hist_already_optional, {"type": "predict_crime_and_punishment"})
    print(f"既に任意質問済み: {result3} (期待値: False)")


if __name__ == "__main__":
    print("ユーザー報告ケースのテストを開始します...\n")

    try:
        test_user_case()
        test_clarification_flow()

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()