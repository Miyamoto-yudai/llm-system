import os, sys
import traceback
import numpy as np
#from tqdm import tqdm
from tqdm import tqdm
import openai
import src.gen.util as util
import time
import src.embedding as emb
import pickle

# make Dataset
def save_ref(target_text :str, target_name, ref_tag :str):
    text = util.remove_newlines_and_spaces(target_text)
    texts = util.splitter(text, 2200)
    for i, text in enumerate(texts):
        em = emb.ada(text)
        d = dict()
        d['text'] = text
        d['emb'] = emb.ada(text)
        d['tag'] = ref_tag
        target_path = str(target_name)+'_'+str(i)+'.ref'
        #print(target_path)
        with open(target_path, 'wb') as f:
            pickle.dump(d, f)
            
def load_ref(target_path):
    with open(target_path, 'rb') as f:
        return pickle.load(f)

# Search
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def similar_refs(query: str, refs, k: int = 3, distance_metric: str = "cosine"):
    """
    refs[0]={'text':text, 'emb':[0.01, -0.02, 0.10]}
    """
    em = emb.ada(query)
    query_embedding = np.array(em)
    for i, ref in enumerate(refs):
        refs[i]['emb'] = np.array(ref['emb'])
    distances = []
    for i, ref in enumerate(refs):
        if distance_metric == "cosine":
            cosine_distance = cosine_similarity(query_embedding, ref['emb'])
            distances.append((i, cosine_distance))
    distances = sorted(distances, key=lambda x: x[1], reverse=True)[:k]
    top_k = [d[0] for d in distances]
    return top_k

