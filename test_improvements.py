#!/usr/bin/env python3
"""
深掘り質問機能の改善テストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat import clarification_manager, reply

def test_question_count():
    """質問数が5-7個になっているかテスト"""
    print("=" * 60)
    print("テスト1: 質問数のテスト")
    print("=" * 60)

    # テスト用の会話履歴
    test_cases = [
        {
            "name": "罪名予測",
            "hist": [{"role": "user", "content": "自動車事故を起こしてしまいました"}],
            "response_type": {"type": "predict_crime_type"}
        },
        {
            "name": "量刑予測",
            "hist": [{"role": "user", "content": "窃盗で逮捕されました"}],
            "response_type": {"type": "predict_punishment"}
        },
        {
            "name": "法プロセス",
            "hist": [{"role": "user", "content": "警察から呼び出しを受けました"}],
            "response_type": {"type": "legal_process"}
        }
    ]

    for case in test_cases:
        print(f"\n【{case['name']}】")
        question = clarification_manager.should_ask_more(case['hist'], case['response_type'])
        if question:
            # 質問数をカウント
            lines = question.split('\n')
            question_lines = [l for l in lines if l.strip().startswith(tuple(str(i) + '.' for i in range(1, 10)))]
            count = len(question_lines)
            print(f"生成された質問数: {count}個")
            print("質問内容:")
            for line in question_lines:
                print(f"  {line}")

            if 5 <= count <= 7:
                print("✓ 質問数は適切です（5-7個）")
            else:
                print(f"✗ 質問数が範囲外です（期待: 5-7個、実際: {count}個）")
        else:
            print("質問が生成されませんでした")

def test_information_sufficiency():
    """十分な情報で質問を終了するかテスト"""
    print("\n" + "=" * 60)
    print("テスト2: 情報充足度チェックのテスト")
    print("=" * 60)

    # 段階的に情報を追加していく会話履歴
    hist = [
        {"role": "user", "content": "交通事故を起こしました"},
        {"role": "assistant", "content": "【確認STEP 1/5】\n状況を把握するため、以下について教えてください。"},
        {"role": "user", "content": "昨日の午後3時頃、交差点で車同士の衝突事故を起こしました。相手の方は軽傷でした。"},
        {"role": "assistant", "content": "【確認STEP 2/5】\n詳細を確認させてください。"},
    ]

    response_type = {"type": "predict_crime_type"}

    # 短い回答での判定
    print("\n短い回答での判定:")
    hist_short = hist + [{"role": "user", "content": "信号を見落としました"}]
    has_sufficient = clarification_manager._has_sufficient_information(hist_short, response_type, 2)
    print(f"情報充足度: {'充分' if has_sufficient else '不足'}")

    # 詳細な回答での判定
    print("\n詳細な回答での判定:")
    hist_detailed = hist + [{"role": "user", "content": """
        信号を見落として交差点に進入してしまい、右側から来た車と衝突しました。
        事故の原因は完全に私の不注意です。相手の方は首を痛めたとのことで病院に行かれました。
        警察の現場検証も終わり、人身事故として処理されることになりました。
        保険会社とも連絡を取り、示談交渉を進める予定です。
        私自身も怪我はありませんが、精神的にショックを受けています。
    """}]
    has_sufficient = clarification_manager._has_sufficient_information(hist_detailed, response_type, 2)
    print(f"情報充足度: {'充分' if has_sufficient else '不足'}")

    if has_sufficient:
        print("✓ 十分な情報があると判定されました")
        question = clarification_manager.should_ask_more(hist_detailed, response_type)
        if question is None:
            print("✓ 追加の質問は生成されませんでした")
        else:
            print("✗ 十分な情報があるのに質問が生成されました")
    else:
        print("まだ情報が不足していると判定されました")

def test_full_conversation():
    """実際の会話フローをテスト"""
    print("\n" + "=" * 60)
    print("テスト3: 完全な会話フローのテスト")
    print("=" * 60)

    hist = []

    # 初回の質問
    user_input = "万引きで捕まってしまいました"
    hist.append({"role": "user", "content": user_input})
    print(f"\nユーザー: {user_input}")

    response = reply(hist)
    print(f"\nシステム: {response}")

    # 質問数をカウント
    if response and "【確認STEP" in response:
        lines = response.split('\n')
        question_lines = [l for l in lines if l.strip().startswith(tuple(str(i) + '.' for i in range(1, 10)))]
        count = len(question_lines)
        print(f"\n初回質問数: {count}個")

        # 2回目の応答
        hist.append({"role": "assistant", "content": response})
        hist.append({"role": "user", "content": "コンビニで500円のお菓子を盗んでしまいました。初犯です。"})

        response2 = reply(hist)
        print(f"\n2回目のシステム応答（一部）: {response2[:200]}...")

        if "【確認STEP" in response2:
            lines2 = response2.split('\n')
            question_lines2 = [l for l in lines2 if l.strip().startswith(tuple(str(i) + '.' for i in range(1, 10)))]
            count2 = len(question_lines2)
            print(f"2回目質問数: {count2}個")

if __name__ == "__main__":
    try:
        test_question_count()
        test_information_sufficiency()
        test_full_conversation()

        print("\n" + "=" * 60)
        print("全てのテストが完了しました")
        print("=" * 60)

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()