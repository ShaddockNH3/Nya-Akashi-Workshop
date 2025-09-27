import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class AkashiChatEngine:
    """
    一个封装了 LLM 加载和纯聊天链的引擎类。
    """
    def __init__(self):
        """
        在实例化时，加载所有必要的模型和组件。
        """
        print("--- 正在初始化聊天引擎... ---")
        self.chat_chain = self._load_chat_chain()
        print("--- ✅ 聊天引擎已准备就绪！ ---")

    def _load_chat_chain(self):
        """
        私有方法，用于加载和构建聊天链。
        """
        print("  - 正在加载 LLM...")
        project_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        model_path = os.path.join(project_base_path, "models/Qwen1.5-7B-Chat")

        model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            torch_dtype=torch.bfloat16, 
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        pipe = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            max_new_tokens=1024, 
            do_sample=True, 
            temperature=0.7, 
            top_p=0.9,
            return_full_text=False
        )
        
        chat_model = HuggingFacePipeline(pipeline=pipe)
        print("  - LLM 加载完成。")
        
        template = """<|system|>
你是一只名叫明石的、来自《碧蓝航线》的秘书舰。你的任务是直接回答指挥官的问题。请在回答时，始终保持明石可爱、略带小恶魔和爱财的口吻。必须使用“喵”、“哦”、“呢”等口癖，并可以加入可爱的颜文字。<|user|>
【指挥官的问题】:
{question}<|assistant|>
【明石的回答】:
"""
        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"question": RunnablePassthrough()}
            | prompt
            | chat_model
            | StrOutputParser()
        )
        return chain

    def get_response_stream(self, question: str):
        """
        对外暴露的方法，用于获取流式响应。
        它会返回一个生成器 (generator)，可以逐块产生文本。
        """
        return self.chat_chain.stream(question)

