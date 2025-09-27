import streamlit as st
import sys
import os

# 1. 获取当前 app.py 文件所在的目录 (也就是 naive_rag 文件夹)
current_dir = os.path.dirname(__file__)
# 2. 从当前目录向上走一级，就得到了项目的根目录 (Akashi 文件夹)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
# 3. 将项目根目录添加到 sys.path 列表的最前面
#    这样 Python 在寻找模块时，就会第一个检查我们的项目文件夹
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------------------------------------------

# 现在，因为项目的根目录已经在“寻宝地图”上了，我们可以使用绝对路径来导入了！
from naive_rag.engine import AkashiChatEngine

# --- 页面基础设置 ---
st.set_page_config(page_title="明石AI 聊天室", page_icon="🐱")
st.title("🐱 明石AI 聊天室 (纯聊流式版)")
st.caption("一个基于 Qwen1.5-7B 的简单对话机器人")

# --- 核心功能 ---
@st.cache_resource
def load_chat_engine():
    """加载聊天引擎的单例函数"""
    engine = AkashiChatEngine()
    return engine

with st.spinner("正在启动明石AI的核心引擎，第一次会有点慢哦..."):
    chat_engine = load_chat_engine()

# --- 对话界面 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("指挥官大人，有什么想问明石的吗？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_stream = chat_engine.get_response_stream(prompt)
        full_response = st.write_stream(response_stream)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
