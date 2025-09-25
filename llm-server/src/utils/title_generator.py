def generate_conversation_title(user_message: str) -> str:
    """
    ユーザーの最初のメッセージから会話タイトルを自動生成する

    Args:
        user_message: ユーザーの最初の発話

    Returns:
        生成されたタイトル（最大30文字）
    """
    # メッセージが短い場合はそのまま使用
    if len(user_message) <= 30:
        return user_message

    # 特定のキーワードから簡潔なタイトルを生成
    keywords_map = {
        "逮捕": "逮捕に関する相談",
        "示談": "示談についての相談",
        "弁護士": "弁護士についての質問",
        "警察": "警察関連の相談",
        "裁判": "裁判についての相談",
        "刑事": "刑事事件の相談",
        "窃盗": "窃盗事件について",
        "暴行": "暴行事件について",
        "詐欺": "詐欺事件について",
        "交通事故": "交通事故の相談",
        "飲酒運転": "飲酒運転について",
        "薬物": "薬物関連の相談",
        "保釈": "保釈についての質問",
        "起訴": "起訴についての相談",
        "前科": "前科についての質問",
        "被害者": "被害者関連の相談",
        "慰謝料": "慰謝料についての相談",
        "執行猶予": "執行猶予について",
        "罰金": "罰金についての質問",
        "懲役": "懲役についての質問",
    }

    # キーワードをチェックしてタイトルを生成
    for keyword, title in keywords_map.items():
        if keyword in user_message:
            return title

    # 句読点で分割して最初の文を使用
    if "。" in user_message:
        first_sentence = user_message.split("。")[0]
        if len(first_sentence) <= 30:
            return first_sentence

    if "？" in user_message:
        first_question = user_message.split("？")[0] + "？"
        if len(first_question) <= 30:
            return first_question

    # それでも長い場合は最初の30文字を使用
    return user_message[:27] + "..."