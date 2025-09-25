import os, sys
import traceback
import numpy as np
#from tqdm import tqdm
from tqdm.notebook import tqdm
import openai
import src.gen.util as util
import time


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def vector_search(
  query: str, 
  embeddings, 
  k: int = 3,
  distance_metric: str = "cosine"
):
  query_embedding = np.array(get_embedding(query))
  
  distances = []
  for i, item_embedding in enumerate(embeddings):
    if distance_metric == "cosine":
      cosine_distance = cosine_similarity(query_embedding, item_embedding)
      distances.append((i, cosine_distance))
  distances = sorted(distances, key=lambda x: x[1], reverse=True)[:k]
  top_k = [d[0] for d in distances]
  return top_k


###

def gen_q(body, m="gpt-3.5-turbo", limit_wc=100):
    resp = openai.ChatCompletion.create(
    model=m,
    #model="gpt-4",
    #model="gpt-3.5-turbo",
    temperature=0,
    stream=False,
    messages=[
        {"role": "system", "content": "以下の文章を答えとする質問を"+str(limit_wc)+"文字以内でできるだけ簡潔に作成してください。"},
        {"role": "user", "content": body}
    ])
    return resp["choices"][0]["message"]["content"]


def gen_summary(body, m="gpt-3.5-turbo"):
    resp = openai.ChatCompletion.create(
    model=m,
    #model="gpt-4",
    #model="gpt-3.5-turbo",
    temperature=0,
    stream=False,
    messages=[
        {"role": "system", "content": "以下の文章を要約してください"},
        {"role": "user", "content": body}
    ])
    return resp["choices"][0]["message"]["content"]


def gen_docs(directory_path, docs={}):
    """
    処理中にAPIエラーなどで止まった場合はdocsの引数を利用してもう一度実行する
    後述のgen_refを使うようにする
    """
    files = [os.path.join(directory_path, name) for name in os.listdir(directory_path)]
    for file in tqdm(files):
        #print("processing",file)
        #file_path = os.path.join(root, file)
        file_path = file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                #print(f'ファイル名: {file_path}')
                #print(f'内容:\n{content}\n{"-"*40}')
                text = util.remove_newlines_and_spaces(content)
                for i, t in enumerate(util.splitter(text, 2200)):
                    file_name = os.path.basename(file_path.replace('.txt', ''))
                    doc_id = file_name+"_"+str(i)
                    if not docs.get(doc_id,None):
                        d = dict()
                        d['body'] = t
                        #file_name = os.path.basename(file_path.replace('条解', '').replace('.txt', ''))
                        d['doc_id'] = doc_id
                        q = gen_q(t)
                        d['q'] = q
                        d['emb'] = get_embedding(q)
                        docs[doc_id] = d
        except Exception:
            traceback.print_exc()
            return docs
    return docs
        
def gen_ref(texts_and_doc_ids, docs={}, debug=False):
    try:
        for item in tqdm(texts_and_doc_ids):
            text, base_doc_id = item
            text = util.remove_newlines_and_spaces(text)
            if debug:
              print("[cleand text]")
              print(text)
            items = util.splitter(text, 2200)
            if debug:
              print("specified item has ", len(items), " items.")
            for i, t in enumerate(items):
                #print(base_doc_id, i)
                if base_doc_id:
                  doc_id = base_doc_id+"_"+str(i)
                  if not docs.get(doc_id,None):
                      d = dict()
                      d['body'] = t
                      if debug:
                          print("processing", doc_id)
                      d['doc_id'] = doc_id
                      q = gen_q(t)
                      d['q'] = q
                      d['emb'] = get_embedding(q)
                      docs[doc_id] = d
                      time.sleep(60)
            if debug:
                print("\n\n\n--------------------------------------\n\n\n")

    except Exception:
            traceback.print_exc()
            return docs
    return docs

def nearest(user_text:str, docs):
    embs = [x['emb'] for x in docs]
    i = vector_search(user_text, embs, k=1)[0]
    return docs[i]

def get_related_doc(docs, doc_id):
    refs = [d for d in docs if d['doc_id'] == doc_id]
    return refs

"""
def reply(m, docs, query):
    d = nearest(query, docs)
    refs = get_related_doc(docs, d['doc_id'])
    return lc.reply(m, refs[0]['body'], query), refs
"""

def print_reply(args):
    rep, refs = args
    for content in rep:
        print(content, end='')
    for ref in refs:
        print("\n",ref['doc_id'])
