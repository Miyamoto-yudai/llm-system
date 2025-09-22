# 罪名予測

import os, sys
import csv
import re
import logging
from pathlib import Path
from importlib import reload

import numpy as np
from tqdm import tqdm_notebook as tqdm

import src.gen.chat as chat
import src.config as config



raw_dir = Path("dataset/raw")

def read_csv(path):
    with open(path, 'r') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            lines.append(','.join(row))
        text = '\n'.join(lines)
        return text

def make_crime_dict():
    targets = ["身体に対する罪","交通に対する罪","居住に対する罪", "偽造に対する罪", "財産に対する罪","名誉に対する罪",
               "自由に対する罪","公共の安全に対する罪","性に対する罪","風俗に対する罪", "国家の作用に対する罪","薬物犯罪",
               "内乱・外患・国交に関する罪","軽犯罪法","ストーカー規制法", "組織犯罪・犯罪収益", "不正アクセス", "日常生活に関する罪"]
    d = {}
    for target in targets:
        filename = '罪名予測テーブル_' + target +'.csv'
        d[target] = read_csv(raw_dir / filename)
    return d
    
    
topics_csv = read_csv(raw_dir / '罪名予測テーブル_大分類.csv')

crime_map = make_crime_dict()

macro_inst = """
あなたは弁護士の代わりに相談者から情報を取得するチャットボットです。
相談者から入力があった場合に、相談者の発話の中から情報を取得し、以下の大分類シートを活用して参照シート名を１つまでに特定してください。
また、特定できない場合は、大分類シートの情報を使用して深掘り質問を相談者に行ってください。
大分類シートは２列目移行に判断基準が記載されおり、◯が該当している場合は行の特定ができるようになっています。
つまり、深掘り質問を行うことで参照シート名の行を１つまでに特定することができます。
深掘り質問を行う場合には、必ず２列目移行のヒアリング項目の表現を使用してください。
深掘り質問が必要ない場合は相談者への回答ではなく「MOVE{参照シート名}」の形式で出力してください。
必要な情報が揃っていない場合でも、現時点で最も可能性の高い候補や追加で確認すべき項目を文章で簡潔にまとめて出力してください。MOVEが特定できない場合は、その理由と不足している情報を箇条書きで示してください。
また回答や質問は相談者に提示する範囲のみとし、途中の思考経路は表示しないようにしてください。

# 大分類シート
""" + topics_csv


def gen(inst, hist):
    client = config.get_openai_client()
    resp = client.chat.completions.create(
        model=config.get_model("main"),
        temperature=config.get_temperature("main"),
        stream=True,
        messages=[{"role": "system", "content": inst}] + hist)
    #return response["choices"][0]["message"]["content"]
    response_text = ""
    for chunk in resp:
        if chunk:
            content = chunk.choices[0].delta.content
            if content:
                response_text += content
                yield content

        
def make_inst(sheet_name, csv):
    inst = """あなたは弁護士の代わりに相談者から情報を取得するチャットボットです。
相談者から入力があった場合に、相談者の発話の中から情報を取得し、以下のシートを活用して罪名の候補を3個以下になるように絞ってください。
シートはcsv形式のファイルとなっており、２列目移行に判断基準が記載され、その列に判断基準において◯がついている罪名に関しては候補になります。
相談者の発言から特定が十分にできていない場合は、相談者に深掘り質問を提示してください。
深掘り質問を行う場合には、必ず２列目移行の判断基準の表現を1つ以上使用してください。
罪名の候補が3個以下になったら、関連する罪名をすべて列挙して教えてください。
必要な情報が不足している場合でも、現時点で判明している事実と不足している判断要素を整理し、追加確認事項を明示してください。
事件概要から罪名が該当した理由は含めないでください。
また回答や質問は相談者に提示する範囲のみとし、途中の思考経路は表示しないようにしてください。

    # シート\n""" + sheet_name + "\n" + csv
    
    return inst

def answer(hist):
    dicision = ''.join(gen(macro_inst, hist))
    print(dicision)
    if not "MOVE" in dicision:
        print("does not move")
        return dicision
    else:
        move_to = dicision.split("MOVE{")[1].split("}")[0].strip()
        target_csv = crime_map.get(move_to)
        if target_csv is None:
            logging.warning("Unknown MOVE target received: %s", move_to)
            return dicision
        inst = make_inst(move_to, target_csv)
        result = gen(inst, hist)
        return result


sample_t="""
"迷惑な話
先日、知り合いが覚せい剤で逮捕され、現在拘留中なのですが、そいつが私から覚せい剤を買ったとか、私も一緒に覚せい剤を使用したとか訳のわからないことを供述しているようなんです。もちろんそんな事実は無く、真っ赤な嘘なのですが、警察から事情を聞きたいので出頭して欲しいと言われています。
私自身、身に憶えの無いことですから警察に出向いて潔白を主張してきます。
そこでご相談ですが、この知り合いに対して偽証罪とか名誉毀損とか訴える方法はありませんでしょうか?
非常に腹が立っています。
よろしくお願い致します。"
"""

#print_reply(answer(sample_t))
