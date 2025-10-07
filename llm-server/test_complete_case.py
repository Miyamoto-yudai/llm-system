#!/usr/bin/env python3
"""
十分な情報を含む本回答生成時に任意質問が付与されるかテスト
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import src.chat as chat


def test_complete_information_case():
    """十分な情報で本回答が生成されるケース"""
    print("=" * 60)
    print("完全な情報での本回答生成テスト")
    print("=" * 60)

    # 初回の相談（情報不足）
    hist1 = [
        {"role": "user", "content": "友人と喧嘩して殴ってしまいました。相手は怪我をしています。"}
    ]

    print("\n【ステップ1: 初回相談（情報不足）】")
    response1 = chat.reply(hist1)
    clarifying_question = ''.join(response1) if not isinstance(response1, str) else response1

    print("深掘り質問が生成されました（省略）")

    # 十分な情報を含む回答
    hist2 = hist1 + [
        {"role": "assistant", "content": clarifying_question},
        {"role": "user", "content": """
以下の詳細情報です：
1. 相手の右手首の骨にヒビが入りました（全治1ヶ月）
2. 昨日の夕方6時頃、自宅近くの公園で起きました
3. 突発的な口論から感情的になって殴ってしまいました。計画性はありません
4. 前科・前歴はありません。初犯です
5. 示談はまだ成立していません。被害者は現時点では処罰感情があります

素手で腕を殴りました。すぐに謝罪はしました。
警察にはまだ届け出ていませんが、相手が診断書を取ったようです。
"""}
    ]

    print("\n【ステップ2: 十分な情報での回答】")
    print("ユーザーが詳細情報を提供...")

    # 本回答の生成
    response2 = chat.reply(hist2)

    full_response = ""
    if isinstance(response2, str):
        full_response = response2
    else:
        for chunk in response2:
            full_response += chunk

    print("\n【本回答（一部）】")
    # 最初の500文字だけ表示
    print(full_response[:500] + "...")

    # 検証
    print("\n" + "=" * 60)
    print("【検証結果】")

    if chat.CLARIFY_PREFIX in full_response:
        print("⚠️ まだ深掘り質問が続いています（情報不足の可能性）")
        return False

    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        print("✅ 任意追加質問が正しく生成されました！")

        # 任意質問部分を表示
        optional_idx = full_response.find(chat.OPTIONAL_FOLLOW_UP_PREFIX)
        print("\n【生成された任意質問】")
        print(full_response[optional_idx:])
        return True
    else:
        print("❌ 本回答なのに任意追加質問が生成されませんでした")
        print("\n【回答の最後の部分】")
        print(full_response[-500:])
        return False


def test_after_multiple_clarifications():
    """複数回の深掘り質問後の本回答"""
    print("\n" + "=" * 60)
    print("複数回の深掘り質問後の本回答テスト")
    print("=" * 60)

    # 実際のユーザーケースに近い履歴を構築
    hist = [
        {"role": "user", "content": "友人と喧嘩して殴ってしまいました。"},
        {"role": "assistant", "content": f"{chat.CLARIFY_PREFIX} 第1回】\n怪我の程度を教えてください"},
        {"role": "user", "content": "骨にヒビが入りました"},
        {"role": "assistant", "content": f"{chat.CLARIFY_PREFIX} 第2回】\n前科はありますか？示談状況は？"},
        {"role": "user", "content": "前科なし、初犯です。示談はまだです。被害者は厳罰希望です。事件は昨日、公園で突発的に起きました。"}
    ]

    print("\n深掘り質問を2回実施後の状況を再現...")

    # 本回答の生成
    response = chat.reply(hist)

    full_response = ""
    if isinstance(response, str):
        full_response = response
    else:
        for chunk in response:
            full_response += chunk

    # 検証
    if chat.CLARIFY_PREFIX in full_response:
        print("⚠️ まだ深掘り質問が続いています")
        return False

    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        print("✅ 複数回の深掘り後でも任意質問が生成されました！")
        return True
    else:
        print("❌ 任意追加質問が生成されませんでした")
        return False


if __name__ == "__main__":
    print("完全情報ケースのテストを開始します...\n")

    try:
        success1 = test_complete_information_case()
        success2 = test_after_multiple_clarifications()

        print("\n" + "=" * 60)
        if success1 and success2:
            print("✅ すべてのテストが成功しました！")
        else:
            print("⚠️ 一部のテストが失敗しました")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()