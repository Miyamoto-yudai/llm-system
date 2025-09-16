import os
import re
import openai
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper, ServiceContext
from llama_index import Document
from llama_index.node_parser import SimpleNodeParser
from langchain import OpenAI
import src.gen.util

def txt_to_doc(directory_path):
    docs = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                #print(f'ファイル名: {file_path}')
                #print(f'内容:\n{content}\n{"-"*40}')
                text = util.remove_newlines_and_spaces(content)
                for i, t in enumerate(util.splitter(text, 2200)):
                    d = Document(t)
                    file_name = os.path.basename(file_path.replace('条解', '').replace('.txt', ''))
                    d.doc_id = file_name+"_"+str(i)
                    docs.append(d)
    return docs


def add_docid(nodes):
    acc = []
    for node in nodes:
        frm = list(node.relationships.values())[0]
        node.doc_id = frm.split("_")[0]
        acc.append(node)
    return acc

def make_nodes(documents):
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    nodes = add_docid(nodes)
    return nodes

def service_context(gpt_type):
    max_input_size = 3000 #5096
    # set number of output tokens
    num_output = 256
    # set maximum chunk overlap
    max_chunk_overlap = 20
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)
    
    llm_predictor = LLMPredictor(llm=OpenAI(
        temperature=0, # 温度
        model_name=gpt_type
        #model_name="gpt-3.5-turbo" # モデル名
        #model_name="gpt-4"
    ))
    
    sc = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    return sc

def make_index(gpt_type, nodes):
    #index = GPTSimpleVectorIndex.from_documents(documents,)# service_context=service_context)
    index = GPTSimpleVectorIndex(nodes, service_context=service_context(gpt_type))
    return index

def save(index, filename):
    index.save_to_disk(filename)
    
def load(gpt_type, filename):
    return GPTSimpleVectorIndex.load_from_disk(filename, service_context=service_context(gpt_type))


def reply(index, q):
    resp = index.query(q)
    ref = []
    for node in resp.source_nodes:
        ref.append(node.doc_id)
    return {"response":resp.response, "ref":ref}
