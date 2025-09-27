import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- 【核心升级】装备“中央导航系统” ---
# 1. 首先，把项目根目录加到“寻路图”里，这样我们才能找到 config
PROJECT_ROOT = "/root/autodl-tmp/Akashi"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. 从 graph_rag 模块中，导入我们唯一的真理来源：config！
try:
    from graph_rag import config
except ImportError:
    print("[致命错误] 无法从 'graph_rag' 模块导入 config！")
    print(" -> 请确保您的项目结构是 Akashi -> graph_rag -> config.py")
    exit()
# ----------------------------------------

# --- 所有的路径和目标，现在都由 config 文件提供！---
VECTOR_STORE_PATH = config.VECTOR_STORE_PATH
EMBEDDING_MODEL_PATH = config.EMBEDDING_MODEL_PATH
TARGET_CHARACTER = "标枪" 

def run_diagnostic():
    print("--- [特种渗透部队 V2] 开始执行底层硬件诊断... ---")
    
    if not os.path.exists(VECTOR_STORE_PATH):
        print(f"[诊断失败] 致命错误：在 '{VECTOR_STORE_PATH}' 找不到数据库文件！")
        return
    print(f"[诊断] 数据库文件存在于: {VECTOR_STORE_PATH}")
    
    # 【新增】诊断 Embedding 模型路径是否存在
    if not os.path.exists(EMBEDDING_MODEL_PATH):
        print(f"[诊断失败] 致命错误：在 '{EMBEDDING_MODEL_PATH}' 找不到 Embedding 模型！")
        return
    print(f"[诊断] Embedding 模型文件夹存在于: {EMBEDDING_MODEL_PATH}")

    try:
        print("[诊断] 正在加载 Embedding 模型...")
        model_kwargs = {'device': 'cuda'}
        embeddings_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_PATH,
            model_kwargs=model_kwargs
        )
        print(" -> Embedding 模型加载成功！")
    except Exception as e:
        print(f"[诊断失败] 致命错误：加载 Embedding 模型失败: {e}")
        return

    try:
        print("[诊断] 正在加载 FAISS 数据库...")
        db = FAISS.load_local(VECTOR_STORE_PATH, embeddings_model, allow_dangerous_deserialization=True)
        print(" -> 数据库加载成功！")
    except Exception as e:
        print(f"[诊断失败] 致命错误：加载数据库失败: {e}")
        return

    print(f"\n--- [核心诊断] 正在尝试以“元数据过滤”模式搜索角色: '{TARGET_CHARACTER}' ---")
    print(f" -> 使用的过滤条件: filter={{'character': '{TARGET_CHARACTER}'}}")
    
    try:
        results = db.similarity_search(
            query="info", k=5, filter={"character": TARGET_CHARACTER}
        )
        
        print("\n--- [诊断结果] ---")
        if results:
            print(f"🎉 [诊断成功!] 找到了 {len(results)} 条关于 '{TARGET_CHARACTER}' 的记录！")
            print(" -> 这意味着数据库和元数据过滤功能【工作正常】！")
            print("\n--- 找到的文档片段预览 ---")
            for i, doc in enumerate(results):
                print(f"  [文档 {i+1}]")
                print(f"    内容预览: {doc.page_content[:100].strip()}...")
                print(f"    元数据: {doc.metadata}")
        else:
            print(f"☠️ [诊断失败!] 未能找到任何关于 '{TARGET_CHARACTER}' 的记录！")
            print(" -> 这意味着问题出在【数据库本身】！")
            print(" -> 请重新运行 `build_database.py`，并检查其日志，确保标枪的元数据被正确写入！")

    except Exception as e:
        print(f"\n☠️ [诊断崩溃!] 在执行搜索时发生了一个意料之外的严重错误: {e}")

if __name__ == "__main__":
    run_diagnostic()
