# 文件路径: agent/tools.py

from langchain.tools import tool
from langchain_community.vectorstores import FAISS
import os
import re
from . import prompts as agent_prompts

# --- 从旧 engine.py 的 retrieve_documents 节点中提炼并拆分 ---

@tool
def character_linker(question: str, name_to_real_name: dict, all_names_list: list) -> str:
    """
    【首选工具】当用户问题可能提到某个舰船的名字、昵称或代号时，必须首先使用此工具来找出其唯一的官方真名。
    这是进行任何角色信息查询的第一步，也是最重要的一步。
    输入是一个问题字符串，输出是找到的官方真名或'未找到'。
    """
    # 这部分逻辑继承自 V7 版本的 identify_character 节点
    for name in all_names_list:
        if name in question:
            real_name = name_to_real_name.get(name)
            return f"成功识别到实体，其官方真名为: {real_name}"
    return "在问题中未识别到任何已知的舰船实体。"

@tool
def character_profile_retriever(character_name: str, character_index: dict) -> str:
    """
    【核心档案工具】当你已经通过 character_linker 工具知道了舰船的官方真名后，使用此工具来获取她完整的个人档案、背景故事和详细数据。
    输入必须是官方真名，输出是完整的档案文本内容。
    """
    # 这部分逻辑继承自旧 engine.py 的 retrieve_documents 的“轨道一”
    if not character_name or character_name == '未找到':
        return "错误：需要一个有效的官方真名才能查询档案。"
    if character_name not in character_index:
        return f"错误：档案库中不存在名为 '{character_name}' 的舰船。"
    
    file_path = character_index[character_name]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 继承 V7 的动态阵营提取
        faction_match = re.search(r'阵营[:：\s]*(.+)', content)
        faction = faction_match.group(1).strip() if faction_match else "未知"
        
        return f"已获取 '{character_name}' 的完整档案 (所属阵营: {faction}):\n\n{content}"
    except Exception as e:
        return f"错误：读取 '{character_name}' 的档案文件失败: {e}"

@tool
def story_database_retriever(query: str, retriever: FAISS.as_retriever, llm, expand_prompt) -> str:
    """
    【剧情深挖工具】用于查询与特定事件、地点、剧情或多个角色关系相关的复杂问题。
    当你需要了解某个故事的来龙去脉，或者一个角色在某个事件中的表现时，使用此工具。
    输入是一个详细的查询语句，输出是相关的剧情片段。
    """
    # 这部分逻辑继承自旧 engine.py 的 retrieve_documents 的“轨道二”，并保留了查询扩展
    if not retriever:
        return "错误：剧情数据库未被加载。"
    
    # 保留查询扩展的精华
    from langchain_core.output_parsers import StrOutputParser
    expand_chain = agent_prompts.EXPAND_PROMPT | llm | StrOutputParser()
    queries_str = expand_chain.invoke({"question": query})
    similar_queries = [q.strip() for q in queries_str.split("\n") if q.strip()]
    all_queries = [query] + similar_queries
    
    all_docs = []
    for q in all_queries:
        all_docs.extend(retriever.invoke(q))
    
    # 去重
    unique_docs = {doc.page_content: doc for doc in all_docs}.values()

    if not unique_docs:
        return "在剧情数据库中未找到相关信息。"
        
    context = "\n---\n".join([f"来源: {doc.metadata.get('source', '未知')}\n内容: {doc.page_content}" for doc in unique_docs])
    return f"从剧情数据库中检索到以下相关片段：\n\n{context}"
