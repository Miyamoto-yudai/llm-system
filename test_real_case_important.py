#!/usr/bin/env python3
"""
実際のケースで重要度の高い質問が生成されるかテスト
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import src.chat as chat


def test_real_case_important_questions():
    """実際のケースで重要な質問が生成されるか確認"""
    print("=" * 60)
    print("実ケースでの重要質問生成テスト")
    print("=" * 60)

    # ユーザーの実例に基づくケース（十分な情報を提供）
    hist = [
        {"role": "user", "content": """
友人と喧嘩して殴ってしまいました。
相手の右手首の骨にヒビが入りました（全治1ヶ月の診断）。
昨日の夕方6時頃、公園で突発的に口論となり、感情的になって素手で殴りました。
初犯で前科はありません。
示談はまだ成立していません。被害者は現在処罰感情があります。
すぐに謝罪しましたが、警察にはまだ届け出ていません。
相手が診断書を取ったようです。
        """}
    ]

    print("\n【入力内容】")
    print("十分な情報を含む傷害事件の相談")

    # 回答を生成
    response = chat.reply(hist)

    full_response = ""
    if isinstance(response, str):
        full_response = response
    else:
        for chunk in response:
            full_response += chunk

    print("\n【生成された回答の概要】")
    # 罪名部分だけ抽出して表示
    if "【罪名予測】" in full_response:
        crime_part = full_response.split("【罪名予測】")[1].split("【")[0][:200]
        print("罪名予測:", crime_part.strip()[:100] + "...")

    if "【量刑予測】" in full_response:
        sentence_part = full_response.split("【量刑予測】")[1].split("【")[0][:200]
        print("量刑予測:", sentence_part.strip()[:100] + "...")

    # 任意追加質問の確認
    print("\n【重要度の高い任意追加質問】")
    if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
        optional_idx = full_response.find(chat.OPTIONAL_FOLLOW_UP_PREFIX)
        optional_part = full_response[optional_idx:]

        print(optional_part)

        # 重要な質問が含まれているかチェック
        print("\n【質問の重要度分析】")

        critical_factors = {
            "執行猶予中": "執行猶予違反で実刑になる可能性",
            "自首": "量刑を3分の1程度軽減可能",
            "正当防衛": "無罪になる可能性",
            "示談金": "処分決定に大きく影響",
            "被害届": "起訴/不起訴の分かれ目",
            "職業": "社会的制裁の程度を判断",
            "治療費": "被害弁償の進捗確認",
            "先に": "正当防衛の可能性",
            "挑発": "情状酌量の余地"
        }

        found_critical = []
        for keyword, impact in critical_factors.items():
            if keyword in optional_part:
                found_critical.append(f"✅ {keyword}: {impact}")

        if found_critical:
            print("発見された重要要素:")
            for item in found_critical:
                print(f"  {item}")
        else:
            print("⚠️ 重要要素が少ない可能性があります")

        # 質問数の確認
        question_count = optional_part.count("\n1.") + optional_part.count("\n2.") + optional_part.count("\n3.") + optional_part.count("\n4.") + optional_part.count("\n5.")
        if question_count > 0:
            question_count = 0
            for i in range(1, 6):
                if f"\n{i}." in optional_part or f" {i}." in optional_part:
                    question_count += 1
            print(f"\n質問数: {question_count}個（推奨: 3-5個）")
            if 3 <= question_count <= 5:
                print("✅ 適切な質問数です")
            else:
                print("⚠️ 質問数が推奨範囲外です")

    else:
        print("❌ 任意追加質問が生成されませんでした")


def test_case_variation():
    """異なるケースでの質問の違いを確認"""
    print("\n" + "=" * 60)
    print("ケース別質問バリエーションテスト")
    print("=" * 60)

    cases = [
        {
            "name": "執行猶予の可能性が高いケース",
            "content": "万引きで捕まりました。被害額1000円、初犯、示談済み、反省しています。"
        },
        {
            "name": "実刑の可能性があるケース",
            "content": "覚醒剤使用で逮捕されました。3回目の逮捕です。前回は執行猶予中でした。"
        },
        {
            "name": "無罪の可能性があるケース",
            "content": "相手から先に殴られたので反撃しました。相手は怪我をしています。"
        }
    ]

    for case in cases:
        print(f"\n【{case['name']}】")
        hist = [{"role": "user", "content": case['content']}]

        response = chat.reply(hist)
        full_response = ""
        if isinstance(response, str):
            full_response = response
        else:
            for chunk in response:
                full_response += chunk

        if chat.OPTIONAL_FOLLOW_UP_PREFIX in full_response:
            optional_idx = full_response.find(chat.OPTIONAL_FOLLOW_UP_PREFIX)
            optional_part = full_response[optional_idx:].split("※")[0]  # 注記より前の質問部分のみ

            # 質問リストを抽出
            lines = optional_part.split('\n')
            questions = [line.strip() for line in lines if line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]

            if questions:
                print("生成された重要質問:")
                for q in questions:
                    print(f"  {q}")
            else:
                print("質問が抽出できませんでした")
        else:
            if chat.CLARIFY_PREFIX in full_response:
                print("（深掘り質問フェーズ中）")
            else:
                print("❌ 任意質問なし")


if __name__ == "__main__":
    print("実ケースでの重要質問生成テストを開始します...\n")

    try:
        test_real_case_important_questions()
        test_case_variation()

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()