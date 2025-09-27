import streamlit as st
import uuid
import sys
import os

# --- 【创世纪·第一法则】(不变) ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from graph_rag.engine import AkashiGraphRAGEngine
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Akashi RAG", page_icon="🐱")
st.title("明石 RAG 问答系统 V6.9 🐱")

@st.cache_resource
def load_rag_engine():
    return AkashiGraphRAGEngine()

rag_engine = load_rag_engine()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": st.session_state.session_id}}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 历史消息渲染 (不变) ---
for msg in st.session_state.messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)
        if hasattr(msg, 'additional_kwargs') and 'detail' in msg.additional_kwargs:
            detail = msg.additional_kwargs['detail']
            with st.expander("🔬 点击展开，回顾本次回答的诊断信息"):
                st.markdown(f"**1. 改写后的独立问题**:\n\n`{detail['standalone_question']}`")
                st.markdown("**2. 检索到的核心情报**:")
                if not detail["documents"]:
                    st.markdown("* (未检索到任何相关文档)*")
                else:
                    for doc in detail["documents"]:
                        doc_type = doc.metadata.get("type", "Story Snippet")
                        st.markdown(f"* **[{doc_type}]** `{doc.metadata.get('source', 'N/A')}`")
                st.markdown(f"**3. 提炼的核心事实**:\n\n```\n{detail['synthesized_facts']}\n```")

if prompt := st.chat_input("指挥官，有什么想问明石的喵？"):
    human_message = HumanMessage(content=prompt)
    st.session_state.messages.append(human_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.expander("🔬 **正在思考中... 点击展开查看实时工作流**", expanded=True):
            log_placeholder = st.empty()
            log_content = ""
        answer_placeholder = st.empty()
        
        final_state = {}
        inputs = {"messages": st.session_state.messages}
        
        # --- 【核心修正】---
        # 我们将循环变量命名为 node_state，因为它就是节点的状态字典
        for node_state in rag_engine.graph.stream(inputs, config=config, stream_mode="values"):
            # 1. 直接检查 'workflow_log' 是否在状态字典中
            if "workflow_log" in node_state and node_state["workflow_log"]:
                latest_log = node_state["workflow_log"][-1]
                log_content += f"{latest_log}\n"
                log_placeholder.text(log_content)

            # 2. 直接用最新的状态字典，来更新我们的最终状态！
            #    删除了所有画蛇添足的错误代码！
            final_state.update(node_state)
        # --------------------

        full_response = final_state.get("generation", "喵？好像出了点问题...")
        answer_placeholder.markdown(full_response)
        
        detail_info = {
            "standalone_question": final_state.get("standalone_question", "N/A"),
            "documents": final_state.get("documents", []),
            "synthesized_facts": final_state.get("synthesized_facts", "N/A"),
        }
        
        ai_message = AIMessage(content=full_response, additional_kwargs={"detail": detail_info})
        st.session_state.messages.append(ai_message)
        st.rerun()
