### **文本摘要 (Summarize Text) 核心方法笔记**

文本摘要的目标是将一篇或多篇长文档内容提炼成简短、精炼的核心摘要。这对于信息检索和快速理解大量文本至关重要。

#### **一、 核心概念与两种主流策略**

构建摘要应用的核心问题是：**如何将可能超出模型上下文窗口长度的文档内容，有效地喂给 LLM？**

主要有两种策略来解决这个问题：

1. **塞入式 (Stuff)**

   * **原理**：最简单直接的方法。将所有文档的文本内容**拼接**起来，一次性地“塞入”到一个 Prompt 中，然后让 LLM 进行单次调用生成摘要。
   * **优点**：实现简单，速度快，能最大限度地保留原文的上下文关联。
   * **缺点**：只适用于文档总长度**小于**模型上下文窗口（Context Window）的情况。对于拥有超长上下文窗口的模型（如 `gpt-4o` 的 128k tokens）非常有效。

2. **Map-Reduce**

   * **原理**：分而治之的策略，分为两步：

     * **Map (映射)**：先将长文档或多个文档**分割**成小块 (chunks)。然后，对**每一个**小块分别调用 LLM，生成一个独立的摘要。
     * **Reduce (规约)**：将上一步生成的所有小摘要**合并**起来，再次调用 LLM，对这些摘要进行“二次摘要”，最终生成一个总的、全局性的摘要。
   * **优点**：可以处理**任意长度**的文档，不受模型上下文窗口的限制。Map 步骤可以并行处理，效率高。
   * **缺点**：在 Map 阶段，每个小块的摘要是独立生成的，可能会丢失块与块之间的上下文关联。

---

#### **二、 方法一：塞入式 (Stuff) 实现**

这是最基础也是最常用的方法，适用于文本量不大的情况。

**步骤 1: 加载文档和选择 LLM**
首先，加载你的文档（如此处的网页内容），并选择一个 LLM。

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain.chat_models import init_chat_model

# 加载文档
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
docs = loader.load()

# 选择 LLM
llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")
```

**步骤 2: 定义 Prompt 和创建 Chain**
创建一个 Prompt 模板，其中 `{context}` 将被替换为所有文档的内容。然后使用 `create_stuff_documents_chain` 这个快捷函数来构建摘要链。

```python
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 定义 Prompt
prompt = ChatPromptTemplate.from_messages(
    [("system", "请为以下内容写一份简洁的摘要：\n\n{context}")]
)

# 实例化 Chain
chain = create_stuff_documents_chain(llm, prompt)
```

**步骤 3: 调用 Chain 生成摘要**
将加载的 `docs` 列表作为 `context` 传入并调用链。

```python
result = chain.invoke({"context": docs})
print(result)

# 也可以流式输出
for token in chain.stream({"context": docs}):
    print(token, end="|")
```

---

#### **三、 方法二：Map-Reduce 实现 (使用 LangGraph)**

当文档非常长时，Map-Reduce 是最佳选择。我们将使用 LangGraph 来编排这个更复杂的流程，因为它能清晰地展示每一步，并支持流式输出和错误恢复。

**核心思想：递归式规约 (Recursive Collapsing)**
为了防止 Reduce 阶段的摘要集合本身也超出上下文窗口，我们采用一种递归式的“折叠”策略：如果摘要集合太长，就先对它们进行一轮摘要，直到总长度达标为止。

**步骤 1: 分割文档**
首先，将长文档切分成多个小块，为 Map 步骤做准备。

```python
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=0
)
split_docs = text_splitter.split_documents(docs)
```

**步骤 2: 定义 Map 和 Reduce 的 Prompts**

* **Map Prompt**: 用于对单个文本块进行摘要。

  ```python
  map_prompt = ChatPromptTemplate.from_messages(
      [("system", "请为以下内容写一份简洁的摘要：\n\n{context}")]
  )
  ```
* **Reduce Prompt**: 用于将多个摘要合并成最终摘要。

  ```python
  reduce_template = """
  以下是一组摘要：
  {docs}
  请将它们提炼成一个关于核心主题的、统一的最终摘要。
  """
  reduce_prompt = ChatPromptTemplate.from_template(reduce_template)
  ```

**步骤 3: 使用 LangGraph 编排流程**
我们将构建一个图来定义整个 Map-Reduce 流程，包括递归规约的逻辑。

1. **定义状态 (State)**：`OverallState` 用于跟踪整个流程的数据，如原始内容、生成的摘要列表和最终摘要。
2. **定义节点 (Nodes)**：

   * `generate_summary`: Map 节点，对单个文本块生成摘要。
   * `collect_summaries`: 将所有 Map 阶段的摘要收集起来。
   * `collapse_summaries`: Reduce 节点，如果摘要总长度超限，则对摘要进行“折叠”。
   * `generate_final_summary`: 最后的 Reduce 节点，生成最终摘要。
3. **定义边 (Edges)**：

   * 使用 `map_summaries` 将所有文本块**分发**到 `generate_summary` 节点。
   * 使用 `should_collapse` 条件边来**判断**是否需要进入 `collapse_summaries` 循环，直到摘要总长度符合要求。

（*注：这里的具体代码较为复杂，核心是利用 LangGraph 的映射、条件边和状态管理功能来实现这个循环和规约的逻辑。*）

**步骤 4: 编译并运行图**
将定义好的图编译成一个可执行的应用，然后传入分割好的文档内容来启动流程。

```python
# 编译图
app = graph.compile()

# 异步流式运行，并观察每一步
async for step in app.astream(
    {"contents": [doc.page_content for doc in split_docs]},
    {"recursion_limit": 10}, # 防止无限循环
):
    print(list(step.keys())) # 打印当前执行的节点名
```

最终，`generate_final_summary` 节点的输出就是我们想要的最终摘要。