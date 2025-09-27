import os

# --- 【唯一真理来源】项目的根目录 ---
# 这个计算逻辑保持不变，它能正确找到 .../Akashi 目录
PROJECT_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# --- 【V8.3 核心修正】定义新的知识库和数据中心的基础路径 ---
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_BASE_PATH, "clean_knowledge")
DATA_PATH = os.path.join(PROJECT_BASE_PATH, "data")

# --- 所有的其他路径，都将基于这些新的基础路径自动生成！---

# --- 模型路径配置 (不变) ---
EMBEDDING_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "models/embedding-model")
LLM_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "models/Qwen1.5-7B-Chat")

# --- 【V8.3 路径校准】数据文件路径 ---

# 向量数据库路径 (位于 data/ 文件夹)
VECTOR_STORE_PATH = os.path.join(DATA_PATH, "faiss_index_story_only")

# 角色索引文件路径 (位于 data/ 文件夹)
CHARACTER_INDEX_PATH = os.path.join(DATA_PATH, "character_index.json")

# 真名/和谐名文件路径 (现在位于 clean_knowledge/ 文件夹！)
NAME_FILE_PATH = os.path.join(KNOWLEDGE_BASE_PATH, "name.json")

# 昵称文件路径 (现在位于 clean_knowledge/ 文件夹！)
NICK_FILE_PATH = os.path.join(KNOWLEDGE_BASE_PATH, "nick.json")


# --- 检索参数配置 (不变) ---
RETRIEVER_K = 10

# 这个print只在第一次导入时执行一次，用于确认
print(f"--- [config.py V8.3] 导航系统已校准，项目根目录锁定为: {PROJECT_BASE_PATH} ---")
