import os

# --- 【唯一真理来源】项目的根目录 ---
# 这段代码会自动计算出 /root/autodl-tmp/Akashi 这个路径
PROJECT_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- 所有的其他路径，都将基于这个根目录自动生成！---

# --- 模型路径配置 ---
# 正确的 Embedding 模型路径
EMBEDDING_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "models/embedding-model")
# 正确的 LLM 模型路径
LLM_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "models/Qwen1.5-7B-Chat") # 假设LLM也在此

# --- 向量数据库路径配置 ---
# 正确的 V2 数据库路径
VECTOR_STORE_PATH = "/root/autodl-tmp/Akashi/data/faiss_index_story_only"

# --- 检索参数配置 ---
RETRIEVER_K = 10

print(f"--- [config.py] 中央导航系统已启动，项目根目录锁定为: {PROJECT_BASE_PATH} ---")
