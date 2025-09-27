import os
import re
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import time
import sys

# --- 装备“中央导航系统” ---
PROJECT_ROOT = "/root/autodl-tmp/Akashi"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
try:
    from graph_rag import config
except ImportError:
    print("[致命错误] 无法从 'graph_rag' 模块导入 config！")
    exit()

def split_profile_document(content, file_name, is_debug=False):
    """
    策略一：角色档案的“精密拆解”
    - is_debug=True 时，会打印出详细的提取日志。
    """
    # 提取角色名
    character_name = file_name.split('_')[-1].replace('.md', '')
    
    # --- 【黑匣子】启动！---
    if is_debug:
        print(f"\n--- [黑匣子] 正在处理文件: {file_name} ---")
        print(f" -> 提取到的角色名: '{character_name}'")

    chunks = content.split('\n### ')
    documents = []
    
    for i, chunk in enumerate(chunks[1:]):
        if not chunk.strip():
            continue
            
        full_chunk_content = "### " + chunk.strip()
        section_title = chunk.split('\n')[0].strip()
        
        doc = Document(page_content=full_chunk_content)
        doc.metadata['source'] = file_name
        doc.metadata['category'] = "角色人设"
        doc.metadata['character'] = character_name
        doc.metadata['section'] = section_title
        
        # --- 【黑匣子】记录每一次的元数据写入！---
        if is_debug:
            print(f"   -> Chunk {i+1} ('{section_title}') -> 生成的元数据: {doc.metadata}")
            
        documents.append(doc)
        
    return documents

# ... (split_story_document 函数不变)
def split_story_document(content, file_name):
    """
    策略二：剧情文档的“场景切分”
    """
    chunks = content.split('\n## ')
    documents = []

    if chunks[0].strip():
        doc = Document(page_content=chunks[0].strip())
        doc.metadata['source'] = file_name
        doc.metadata['category'] = "剧情"
        doc.metadata['scene'] = "序幕"
        documents.append(doc)

    for chunk in chunks[1:]:
        if not chunk.strip():
            continue
            
        full_chunk_content = "## " + chunk.strip()
        scene_title = chunk.split('\n')[0].strip()
        
        doc = Document(page_content=full_chunk_content)
        doc.metadata['source'] = file_name
        doc.metadata['category'] = "剧情"
        doc.metadata['scene'] = scene_title
        documents.append(doc)

    return documents

def load_and_split_documents(knowledge_base_path, is_debug=False):
    print(f"\n[V2.2] [步骤 1/4] 开始加载并进行“智能颗粒度”切分...")
    all_docs = []
    profile_folder = "ships"
    
    for folder_name in os.listdir(knowledge_base_path):
        directory = os.path.join(knowledge_base_path, folder_name)
        if not os.path.isdir(directory):
            continue
            
        print(f"  -> 正在处理文件夹: '{folder_name}'")
        md_files = [f for f in os.listdir(directory) if f.endswith('.md')]

        for file_name in md_files:
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # --- 传递 debug 信号 ---
                if folder_name == profile_folder:
                    docs = split_profile_document(content, file_name, is_debug)
                else:
                    docs = split_story_document(content, file_name)
                
                all_docs.extend(docs)

            except Exception as e:
                print(f"\n[错误] 处理文件 {file_path} 失败: {e}")

    print(f"\n[成功] 总共加载并切分出 {len(all_docs)} 个知识块！")
    return all_docs

# ... (create_vector_store 函数不变)
def create_vector_store(docs, save_path, model_name):
    if not docs:
        print("[错误] 没有知识块可以用于建造数据库。")
        return
    print("\n[步骤 2/4] 启动 Embedding 模型...")
    model_kwargs = {'device': 'cuda'}
    embeddings_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs
    )
    print("\n[步骤 3/4] 开始向量化并存入数据库...")
    start_time = time.time()
    vector_store = FAISS.from_documents(docs, embeddings_model)
    end_time = time.time()
    print(f"-> 数据库向量化完成！耗时: {end_time - start_time:.2f} 秒")
    
    data_directory = os.path.dirname(save_path)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    print(f"\n[步骤 4/4] 正在保存数据库...")
    vector_store.save_local(save_path)
    print(f"\n🎉 V2.2 数据库已保存在: '{save_path}'")


if __name__ == "__main__":
    KNOWLEDGE_BASE_PATH = os.path.join(config.PROJECT_BASE_PATH, "clean_knowledge")
    VECTOR_STORE_PATH = config.VECTOR_STORE_PATH
    EMBEDDING_MODEL_PATH = config.EMBEDDING_MODEL_PATH
    
    # --- 启动“黑匣子”模式 ---
    all_documents = load_and_split_documents(KNOWLEDGE_BASE_PATH, is_debug=True)
    
    if all_documents:
        create_vector_store(all_documents, VECTOR_STORE_PATH, EMBEDDING_MODEL_PATH)

