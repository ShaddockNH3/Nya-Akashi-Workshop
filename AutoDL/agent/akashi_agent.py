# 文件路径: agent/akashi_agent.py

import os
import json
import torch
from transformers import BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain_core.messages import AIMessage, HumanMessage

# 继承并使用 config.py 和新的 prompts/tools
from . import config
from . import prompts as agent_prompts
from .tools import character_linker, character_profile_retriever, story_database_retriever

class AkashiAgent:
    def __init__(self):
        print("--- [Agent V8.0 思考驱动] 正在初始化『宗师级工匠-茗』... ---")
        # 继承旧 engine.py 的加载逻辑
        self._load_foundations()
        # 创建工具箱
        self.tools = self._create_tools()
        # 创建能驱动工具的执行器
        self.agent_executor = self._create_agent_executor()
        print("--- ✅ 『宗师级工匠-茗』已准备就绪！ ---")

    def _load_foundations(self):
        # 这部分代码几乎完全从旧 engine.py 的 _load_components 继承而来
        quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        self.llm = HuggingFacePipeline.from_model_id(model_id=config.LLM_MODEL_PATH, task="text-generation", device_map="auto", model_kwargs={"torch_dtype": torch.bfloat16, "quantization_config": quantization_config}, pipeline_kwargs={"max_new_tokens": 1024, "return_full_text": False})
        embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_PATH, model_kwargs={'device': 'cuda'})
        
        # 继承 V7 的别名加载逻辑
        name_file = config.NAME_FILE_PATH
        nick_file = config.NICK_FILE_PATH
        self.name_to_real_name = {}
        all_names = []
        with open(name_file, 'r', encoding='utf-8') as f: name_data = json.load(f)
        for r, h in name_data.items():
            self.name_to_real_name[r] = r; self.name_to_real_name[h] = r; all_names.extend([r, h])
        with open(nick_file, 'r', encoding='utf-8') as f: nick_data = json.load(f)
        for r, n_list in nick_data.items():
            for n in n_list: self.name_to_real_name[n] = r; all_names.append(n)
        self.all_names_list = sorted(list(set(all_names)), key=len, reverse=True)

        index_file = config.CHARACTER_INDEX_PATH
        with open(index_file, 'r', encoding='utf-8') as f: self.character_index = json.load(f)

        db_path = config.VECTOR_STORE_PATH
        db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        self.story_retriever = db.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
        print(" -> 所有基础零件加载完毕！")

    def _create_tools(self):
        # 依赖注入，将加载好的资源“装配”到工具上
        character_linker.args = {"name_to_real_name": self.name_to_real_name, "all_names_list": self.all_names_list}
        character_profile_retriever.args = {"character_index": self.character_index}
        story_database_retriever.args = {"retriever": self.story_retriever, "llm": self.llm, "expand_prompt": agent_prompts.EXPAND_PROMPT}
        
        print(" -> 工具箱已装配完成！")
        return [character_linker, character_profile_retriever, story_database_retriever]

    def _create_agent_executor(self):
        rendered_tools = render_text_description(self.tools)
        prompt = PromptTemplate(
            input_variables=["chat_history", "input", "agent_scratchpad"],
            template=agent_prompts.REACT_PROMPT_TEMPLATE,
            partial_variables={"tools": rendered_tools, "tool_names": ", ".join([t.name for t in self.tools])}
        )
        agent = create_react_agent(self.llm, self.tools, prompt)
        print(" -> Agent思考核心已构建！")
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors="请检查你的行动格式，确保Action和Action Input是正确的。")

    def invoke(self, user_input: str, chat_history: list):
        history_str = "\n".join([f"{'指挥官' if isinstance(msg, HumanMessage) else '明石'}: {msg.content}" for msg in chat_history])
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": history_str
        })
        return response['output']
