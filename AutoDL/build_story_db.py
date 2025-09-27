import os
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import time
import sys

# 导入我们的中央导航系统
PROJECT_ROOT = "/root/autodl-tmp/Akashi"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
try:
    from graph_rag import config
except ImportError:
    print("[致命错误] 无法从 'graph_rag' 模块导入 config！")
    exit()

def split_story_document(content, file_name):
    # (这个函数和之前一样，专门用来切分剧情文件)
    chunks = content.split('\n## ')
    documents = []
    if chunks[0].strip():
        doc = Document(page_content=chunks[0].strip(), metadata={'source': file_name, 'category': '剧情', 'scene': '序幕'})
        documents.append(doc)
    for chunk in chunks[1:]:
        if not chunk.strip(): continue
        full_chunk_content = "## " + chunk.strip()
        scene_title = chunk.split('\n')[0].strip()
        doc = Document(page_content=full_chunk_content, metadata={'source': file_name, 'category': '剧情', 'scene': scene_title})
        documents.append(doc)
    return documents

def build_story_only_vector_store():
    """
    全新的生产线！它将只处理除了'ships'之外的所有文件夹，
    创建一个纯净的、只包含剧情和背景资料的向量数据库。
    """
    print("--- [凤凰涅槃计划] 开始建造“剧情专用”向量数据库... ---")
    KNOWLEDGE_BASE_PATH = os.path.join(config.PROJECT_BASE_PATH, "clean_knowledge")
    # 【核心】为新的数据库指定一个全新的、不会混淆的路径！
    STORY_DB_PATH = os.path.join(config.PROJECT_BASE_PATH, "data", "faiss_index_story_only")
    
    all_story_docs = []
    
    for folder_name in os.listdir(KNOWLEDGE_BASE_PATH):
        # 【核心逻辑】跳过 'ships' 文件夹！
        if folder_name == 'ships':
            print(f" -> 已跳过角色人设文件夹: '{folder_name}'")
            continue
            
        directory = os.path.join(KNOWLEDGE_BASE_PATH, folder_name)
        if not os.path.isdir(directory): continue
            
        print(f"  -> 正在处理剧情文件夹: '{folder_name}'")
        md_files = [f for f in os.listdir(directory) if f.endswith('.md')]
        for file_name in tqdm(md_files, desc=f"    切分 {folder_name} 中的文件"):
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                docs = split_story_document(content, file_name)
                all_story_docs.extend(docs)
            except Exception as e:
                print(f"\n[错误] 处理文件 {file_path} 失败: {e}")

    if not all_story_docs:
        print("\n[警告] 未能加载到任何剧情文档！")
        return
        
    print(f"\n[成功] 共加载并切分出 {len(all_story_docs)} 个“高纯度”剧情知识块！")
    
    print("\n[步骤 2/3] 启动 Embedding 模型...")
    embeddings_model = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_PATH,
        model_kwargs={'device': 'cuda'}
    )
    
    print("\n[步骤 3/3] 开始将剧情知识块存入“深海声呐阵列”...")
    start_time = time.time()
    vector_store = FAISS.from_documents(all_story_docs, embeddings_model)
    end_time = time.time()
    print(f"-> 数据库向量化完成！耗时: {end_time - start_time:.2f} 秒")
    
    vector_store.save_local(STORY_DB_PATH)
    print(f"\n🎉 作战成功！“剧情专用”数据库已保存在: '{STORY_DB_PATH}'")

if __name__ == "__main__":
    build_story_only_vector_store()

