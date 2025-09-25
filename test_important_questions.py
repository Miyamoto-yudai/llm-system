#!/usr/bin/env python3
"""
重要度の高い任意追加質問の生成テスト
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import src.chat as chat


def test_important_questions_generation():
    """重要な質問が生成されるかテスト"""
    print("=" * 60)
    print("重要度の高い任意追加質問生成テスト")
    print("=" * 60)

    test_cases = [
        {
            "name": "傷害事件のケース",
            "history": [
                {"role": "user", "content": """
友人と喧嘩して殴ってしまいました。詳細は以下の通りです：
- 相手は右手首骨折（全治1ヶ月）
- 昨日の夕方、公園で突発的に発生
- 素手で殴打、計画性なし
- 初犯、前科なし
- 示談未成立、被害者は処罰感情あり
- すぐに謝罪済み
                """}
            ],
            "expected_topics": ["執行猶予中", "自首", "治療費", "示談金額", "職業への影響"]
        },
        {
            "name": "飲酒運転のケース",
            "history": [
                {"role": "user", "content": """
飲酒運転で事故を起こしました：
- 呼気アルコール濃度0.3mg
- 歩行者に骨折の怪我（全治3ヶ月）
- 信号無視あり
- 初犯です
- 示談交渉中
- 被害者は厳罰希望
                """}
            ],
            "expected_topics": ["酒酔い運転", "救護義務", "免許取消", "示談金額", "保険"]
        },
        {
            "name": "窃盗のケース",
            "history": [
                {"role": "user", "content": """
コンビニで商品を万引きしました：
- 被害額3000円
- 防犯カメラに映っている
- 店員に見つかり警察を呼ばれた
- 初犯
- その場で謝罪し商品代金は支払い済み
                """}
            ],
            "expected_topics": ["常習性", "余罪", "示談", "被害届取り下げ", "生活困窮"]
        }
    ]

    for case in test_cases:
        print(f"\n【テストケース: {case['name']}】")
        print(f"相談内容: {case['history'][0]['content'][:100]}...")

        # 本回答を生成（ここでは簡易的にシミュレート）
        response_text = """
【罪名予測】
傷害罪（刑法204条）が成立します。

【量刑予測】
懲役6ヶ月〜2年（執行猶予付きの可能性）
または罰金20〜50万円

【量刑判断の根拠】
- 初犯であること
- 計画性がないこと
- 被害者の処罰感情があること
        """

        # 任意質問を生成
        manager = chat.optional_follow_up_manager
        optional_questions = manager.generate_optional_questions(
            case['history'],
            {"type": "predict_crime_and_punishment"},
            response_text
        )

        if optional_questions:
            print("\n生成された任意追加質問:")
            print(optional_questions)

            # 期待されるトピックが含まれているか確認
            print("\n重要トピックのカバー状況:")
            for topic in case['expected_topics']:
                if topic in optional_questions:
                    print(f"  ✅ {topic}")
                else:
                    print(f"  ⚠️ {topic} (含まれていない可能性)")
        else:
            print("❌ 任意質問が生成されませんでした")

        print("-" * 40)


def test_question_importance_sorting():
    """質問の重要度によるソートをテスト"""
    print("\n" + "=" * 60)
    print("質問重要度ソーティングテスト")
    print("=" * 60)

    # 実際のケースで重要度の高い質問が優先されるか確認
    hist = [
        {"role": "user", "content": "傷害事件を起こしました。初犯です。"},
        {"role": "assistant", "content": "詳細を教えてください"},
        {"role": "user", "content": """
被害者は全治2週間の打撲です。
示談はまだです。
謝罪はしました。
前科はありませんが、以前にも喧嘩で警察沙汰になったことがあります。
        """}
    ]

    print("シナリオ: 傷害事件（詳細情報提供後）")

    response = chat.reply(hist)
    full_response = ""
    if isinstance(response, str):
        full_response = response
    else:
        for chunk in response:
            full_response += chunk

    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        optional_part = full_response.split(chat.OPTIONAL_FOLLOW_UP_PREFIX)[1]
        print("\n生成された重要度の高い質問:")
        print(chat.OPTIONAL_FOLLOW_UP_PREFIX + optional_part)

        # 重要な要素が含まれているか確認
        important_keywords = ["執行猶予", "前歴", "示談金", "被害届", "職業"]
        print("\n重要キーワードのチェック:")
        for keyword in important_keywords:
            if keyword in optional_part:
                print(f"  ✅ {keyword} が含まれています")
    else:
        print("❌ 任意質問が生成されませんでした")


if __name__ == "__main__":
    print("重要度の高い任意追加質問のテストを開始します...\n")

    try:
        test_important_questions_generation()
        test_question_importance_sorting()

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()