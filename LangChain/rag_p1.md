### **构建检索增强生成 (RAG) 应用笔记 (Part 1)**

RAG (Retrieval Augmented Generation) 是一种强大的技术，它将信息检索与大语言模型 (LLM) 的生成能力相结合，使得应用能够基于特定的外部知识源来回答问题。

#### **一、 RAG 核心架构**

一个典型的 RAG 应用包含两个主要阶段：

1. **索引 (Indexing) - 离线阶段**

   * 这是一个预处理流程，负责从数据源（如网站、文档）提取信息并建立一个可供快速检索的索引。
   * **完整流程**：**加载 (Load)** -> **分割 (Split)** -> **存储 (Store)**。

2. **检索与生成 (Retrieval and Generation) - 实时阶段**

   * 当用户提出问题时，应用会执行此流程。
   * **完整流程**：**检索 (Retrieve)** -> **生成 (Generate)**。

---

#### **二、 环境设置与核心组件**

**1. 安装必要库**

```bash
%pip install --quiet --upgrade langchain-text-splitters langchain-community langgraph "langchain[google-genai]" langchain-openai
```

**2. (可选) 配置 LangSmith**
用于追踪和调试应用，随着应用变复杂会非常有用。

```python
import getpass
import os

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("请输入您的 LangSmith API Key: ")
```

**3. 选择核心组件**

* **聊天模型 (Chat Model)**：用于最终生成答案。

  ```python
  from langchain.chat_models import init_chat_model
  llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")
  ```
* **嵌入模型 (Embeddings Model)**：用于将文本转换为向量。

  ```python
  from langchain_openai import OpenAIEmbeddings
  embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
  ```
* **向量存储 (Vector Store)**：用于存储和检索向量。

  ```python
  from langchain_core.vectorstores import InMemoryVectorStore
  vector_store = InMemoryVectorStore(embeddings)
  ```

---

#### **三、 详细步骤 1：索引 (Indexing)**

以抓取 Lilian Weng 的一篇博客文章为例。

**步骤 1.1: 加载文档 (Loading Documents)**
使用 `WebBaseLoader` 从指定 URL 加载网页内容。可以通过 `bs_kwargs` 精准控制只解析特定的 HTML 标签，以获取最相关的内容。

```python
import bs4
from langchain_community.document_loaders import WebBaseLoader

# 创建一个过滤器，只保留文章标题、头部和正文内容
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()
```

**步骤 1.2: 分割文档 (Splitting Documents)**
原始文档太长，需要切分成小块，以便于模型处理和精准检索。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 每个块的大小
    chunk_overlap=200,    # 块之间的重叠部分
    add_start_index=True  # 记录在原文中的起始位置
)
all_splits = text_splitter.split_documents(docs)
```

**步骤 1.3: 存储文档 (Storing Documents)**
将分割后的文本块进行嵌入，并存入之前实例化的向量库中，完成索引的建立。

```python
# 这一个命令会完成所有文本块的嵌入和存储
document_ids = vector_store.add_documents(documents=all_splits)
```

至此，索引阶段完成！我们已经拥有了一个包含博客文章内容、可供查询的向量库。

---

#### **四、 详细步骤 2：检索与生成 (Retrieval and Generation)**

我们将使用 `LangGraph` 来编排检索和生成的流程，这样做可以轻松支持同步、异步、流式调用，并且便于后续扩展。

**步骤 2.1: 定义应用状态 (State)**
`State` 用于在流程的各个节点之间传递数据。对于一个简单的 RAG，我们需要跟踪问题、检索到的上下文和最终答案。

```python
from langchain_core.documents import Document
from typing_extensions import List, TypedDict

class State(TypedDict):
    question: str          # 用户问题
    context: List[Document] # 检索到的文档列表
    answer: str            # LLM 生成的答案
```

**步骤 2.2: 定义应用节点 (Nodes)**
节点是流程中的具体步骤。我们定义两个核心节点：`retrieve` 和 `generate`。

```python
from langchain import hub

# 从 LangChain Hub 加载一个预设的 RAG 提示模板
prompt = hub.pull("rlm/rag-prompt")

# 节点1: 检索
def retrieve(state: State):
    """根据问题从向量库中检索相关文档。"""
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

# 节点2: 生成
def generate(state: State):
    """将问题和检索到的上下文传给 LLM 生成答案。"""
    # 将文档列表格式化为单一字符串
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    # 调用提示模板
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    # 调用 LLM
    response = llm.invoke(messages)
    return {"answer": response.content}
```

**步骤 2.3: 定义控制流 (Control Flow)**
使用 `StateGraph` 将各个节点连接起来，形成一个完整的执行图。

```python
from langgraph.graph import START, StateGraph

# 构建图
graph_builder = StateGraph(State)
# 添加一个顺序执行的链条：先执行 retrieve，再执行 generate
graph_builder.add_sequence([retrieve, generate])
# 定义起始节点
graph_builder.add_edge(START, "retrieve")
# 编译图，得到可执行的应用
graph = graph_builder.compile()
```

**步骤 2.4: 调用应用**
编译完成后，就可以像调用普通函数一样来使用这个 RAG 应用了。

```python
# 同步调用
response = graph.invoke({"question": "What is Task Decomposition?"})
print(response["answer"])

# 流式调用，可以观察每个节点的输出
for step in graph.stream({"question": "What is Task Decomposition?"}, stream_mode="updates"):
    print(f"{step}\n\n----------------\n")
```