# --- 完整的“零件图纸”清单 (不变) ---
import torch, re, warnings, os, json
from typing import List, TypedDict
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from . import config, prompts

warnings.filterwarnings("ignore")

class GraphState(TypedDict):
    messages: list; question: str; standalone_question: str; documents: List[Document]
    synthesized_facts: str; generation: str; workflow_log: List[str]; _route_decision: str

class AkashiGraphRAGEngine:
    def __init__(self):
        print("--- [V6.5 语法修正] 初始化『纯净双轨情报系统』引擎... ---")
        self._load_components()
        self.graph = self._build_graph()
        print("--- ✅ RAG引擎 V6.5 已准备就绪 ---")

    def _load_character_list_and_index(self):
        print("--- 正在加载『皇家档案馆』全舰船名录与索引... ---")
        # 【语法修正】将 print 和 try 分开写在两行！
        try:
            index_file_path = os.path.join(config.PROJECT_BASE_PATH, "data", "character_index.json")
            with open(index_file_path, 'r', encoding='utf-8') as f: self.character_index = json.load(f)
            self.character_list = list(self.character_index.keys())
            print(f" -> 成功加载 {len(self.character_list)} 位舰船名录与索引！")
        except Exception as e:
            print(f"[致命错误] 加载『皇家档案馆』失败: {e}!")
            self.character_index = {}; self.character_list = []

    def _load_components(self):
        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        self.llm = HuggingFacePipeline.from_model_id(model_id=config.LLM_MODEL_PATH, task="text-generation", device_map="auto", model_kwargs={"torch_dtype": torch.bfloat16, "quantization_config": quantization_config}, pipeline_kwargs={"max_new_tokens": 1024, "return_full_text": False})
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_PATH, model_kwargs={'device': 'cuda'})
        self._load_character_list_and_index()
        STORY_DB_PATH = os.path.join(config.PROJECT_BASE_PATH, "data", "faiss_index_story_only")
        print(f"--- 正在从 '{STORY_DB_PATH}' 加载“剧情专用”数据库... ---")
        # 【语法修正】将 print 和 try 分开写在两行！
        try:
            db = FAISS.load_local(STORY_DB_PATH, embeddings, allow_dangerous_deserialization=True)
            self.story_retriever = db.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
            print(" -> “剧情专用”数据库加载成功！")
        except Exception as e:
            print(f"[致命错误] 加载“剧情专用”数据库失败: {e}!")
            self.story_retriever = None

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        workflow.add_node("route_query", self.route_query)
        # (后续的 build_graph 内容，为了简洁，省略粘贴，因为它们完全没有变化)
        workflow.add_node("rewrite_question", self.rewrite_question); workflow.add_node("retrieve_documents", self.retrieve_documents); workflow.add_node("filter_documents", self.filter_documents); workflow.add_node("synthesize_facts", self.synthesize_facts); workflow.add_node("generate_answer", self.generate_answer); workflow.add_node("direct_chat", self.direct_chat); workflow.set_entry_point("route_query"); workflow.add_conditional_edges("route_query", self.decide_route, {"RAG": "rewrite_question", "CHAT": "direct_chat"}); workflow.add_edge("rewrite_question", "retrieve_documents"); workflow.add_edge("retrieve_documents", "filter_documents"); workflow.add_edge("filter_documents", "synthesize_facts"); workflow.add_edge("synthesize_facts", "generate_answer"); workflow.add_edge("generate_answer", END); workflow.add_edge("direct_chat", END); return workflow.compile(checkpointer=MemorySaver())

    # (route_query, decide_route, rewrite_question 等所有后续函数，都完全不变)
    def route_query(self, state: GraphState):
        log = "STEP 1: 判断对话类型..."; messages = state['messages']; current_question_message = messages[-1]; question_content = current_question_message.content; history_messages = messages[:-1]; history = "\n".join([f"{msg.type}: {msg.content}" for msg in history_messages]); chain = prompts.ROUTE_PROMPT | self.llm | StrOutputParser(); route_decision = chain.invoke({"chat_history": history, "question": question_content}); decision = "RAG" if "RAG" in route_decision else "CHAT"; return {"workflow_log": [log], "_route_decision": decision, "question": question_content}
    def decide_route(self, state: GraphState):
        log = f"  -> 决策结果: {state['_route_decision']}"; print(log); return state['_route_decision']
    def rewrite_question(self, state: GraphState):
        log = "STEP 2 (RAG): 改写问题以包含上下文..."; question_content = state['question']; history = "\n".join([f"{msg.type}: {msg.content}" for msg in state['messages'][:-1]]); chain = prompts.REWRITE_PROMPT | self.llm | StrOutputParser(); standalone_question = chain.invoke({"chat_history": history, "question": question_content}); return {"standalone_question": standalone_question, "workflow_log": state['workflow_log'] + [log]}
    def retrieve_documents(self, state: GraphState):
        log_entry = "STEP 3 (RAG): [V6.0 强制索敌 + 纯净RAG] 执行..."; print(log_entry); question = state['standalone_question']; character_docs = []; story_docs = []
        found_names = [name for name in self.character_list if name in question]
        if found_names:
            print(f"  -> [轨道一：档案馆] 强制锁定目标: {found_names}")
            for name in found_names:
                file_path = self.character_index[name]
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                    doc = Document(page_content=content, metadata={"source": os.path.basename(file_path), "type": "Character Profile"})
                    character_docs.append(doc); print(f"    -> 命中！已从档案馆加载 '{name}' 的完整档案！")
                except Exception as e: print(f"    -> [错误] 读取 '{file_path}' 失败: {e}")
        else: print("  -> [轨道一：档案馆] 未在问题中强制匹配到任何舰船。")
        if self.story_retriever:
            print("  -> [轨道二：声呐阵列] 在“剧情专用”数据库中进行语义搜索...")
            expand_chain = prompts.EXPAND_PROMPT | self.llm | StrOutputParser(); queries_str = expand_chain.invoke({"question": question})
            similar_queries = [q.strip() for q in queries_str.split("\n") if q.strip()]; all_queries = [question] + similar_queries
            for query in all_queries: story_docs.extend(self.story_retriever.invoke(query))
        final_docs = {doc.page_content: doc for doc in character_docs + story_docs}
        print(f"  -> [情报汇总] 共找到 {len(final_docs)} 份不重复的相关情报 ({len(character_docs)}份人设, {len(story_docs)}份剧情)。")
        return {"documents": list(final_docs.values()), "workflow_log": state['workflow_log'] + [log_entry]}
    def filter_documents(self, state: GraphState):
        log_entry = "STEP 3.5 (RAG): [质检] 过滤不相关的检索结果..."; print(log_entry); question = state['standalone_question']; documents = state['documents']; filter_chain = prompts.FILTER_PROMPT | self.llm | StrOutputParser(); filtered_docs = []
        for doc in documents:
            try:
                score_str = filter_chain.invoke({"question": question, "document": doc.page_content}); score_match = re.search(r'\d+', score_str)
                if score_match:
                    score = int(score_match.group(0))
                    if score >= 4: filtered_docs.append(doc)
            except Exception as e: print(f"  -> [警告] 质检打分失败: {e}"); continue
        print(f"  -> [质检] 完成，过滤出 {len(filtered_docs)} 份高相关度情报。"); return {"documents": filtered_docs, "workflow_log": state['workflow_log'] + [log_entry]}
    def synthesize_facts(self, state: GraphState):
        log_entry = "STEP 4 (RAG): 分析资料，提炼核心事实..."; print(log_entry); chain = prompts.SYNTHESIZE_PROMPT | self.llm | StrOutputParser()
        if not state['documents']: print("  -> [情报] 无可用文档，判定为无核心事实。"); facts = "无核心事实可总结。"
        else: context = "\n---\n".join([doc.page_content for doc in state['documents']]); facts = chain.invoke({"context": context, "question": state['standalone_question']})
        return {"synthesized_facts": facts, "workflow_log": state['workflow_log'] + [log_entry]}
    def generate_answer(self, state: GraphState):
        log = "STEP 5 (RAG): 基于核心事实生成回答..."; chain = prompts.GENERATION_PROMPT | self.llm | StrOutputParser(); generation = chain.invoke({"context": state['synthesized_facts'], "question": state['standalone_question']}); return {"generation": generation, "workflow_log": state['workflow_log'] + [log]}
    def direct_chat(self, state: GraphState):
        log = "STEP 2 (CHAT): 进行纯聊天回复..."; question_content = state['question']; chain = prompts.CHAT_PROMPT | self.llm | StrOutputParser(); generation = chain.invoke({"question": question_content}); return {"generation": generation, "workflow_log": state['workflow_log'] + [log]}

