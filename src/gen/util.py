import re
import pickle
import tiktoken
from tiktoken.core import Encoding


encoding: Encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
def tc(body):
    return len(encoding.encode(body))
#encoding # gpt-4でもcl100k_baseで良い


def remove_newlines_and_spaces(text):
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        if re.match(r'^[\d①②③④⑤⑥⑦⑧⑨⑩]', line.strip()):
            cleaned_lines.append('\n' + line.strip().replace(" ", ""))
        else:
            cleaned_lines.append(line.strip().replace(" ", ""))

    return "".join(cleaned_lines)
#text = remove_newlines_and_spaces(example)

def splitter(arr, size):
    return [arr[i:i+size] for i in range(0, len(arr), size)]

def save(obj, filepath):
    with open(filepath, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load(filepath):
    with open(filepath, 'rb') as handle:
        return pickle.load(handle)

def print_reply(content):
    for c in content:
        print(c, end='')
