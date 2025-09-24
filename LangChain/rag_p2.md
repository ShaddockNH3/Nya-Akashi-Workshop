### **构建可对话的 RAG 应用笔记 (Part 2)**

在 Part 1 的基础上，本笔记将专注于为 RAG 应用添加**对话记忆**，使其能够理解上下文，并支持多轮问答。我们将探索两种主流的实现方法：“链 (Chains)” 和 “代理 (Agents)”。

#### **一、 核心目标：赋予 RAG 对话能力**

让应用能够：

1. **记住历史消息**：理解后续问题与之前对话的关联。
2. **上下文改写查询**：例如，当用户问“它有哪些常见的实现方式？”时，能结合上一轮的“任务分解”主题，生成更精确的检索查询，如“任务分解的常见实现方式”。
3. **支持多步检索**：对于复杂问题，能够自主进行多次检索来收集完整信息。

---

#### **二、 方法一：构建对话式“链” (Chain)**

这种方法结构清晰，执行流程相对固定（每轮对话最多执行一次检索），非常适合构建稳定可预测的问答机器人。

**核心思想**：利用现代 LLM 的 **工具调用 (Tool-calling)** 能力，将信息检索看作一个可供 LLM 调用的“工具”。

**步骤 1: 将检索包装为“工具” (Tool)**
我们不再直接调用检索函数，而是用 `@tool` 装饰器把它包装起来。这样，LLM 就可以在需要时“决定”调用这个工具，并生成合适的查询语句。

```python
from langchain_core.tools import tool

@tool
def retrieve(query: str):
    """根据查询检索相关信息。"""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    # ... (省略了格式化部分)
    return serialized_docs, retrieved_docs
```

**步骤 2: 使用 `MessagesState` 管理状态**
为了更好地处理对话流，我们不再使用 Part 1 中的自定义 `TypedDict`，而是采用 LangGraph 内置的 `MessagesState`。它可以方便地将整个对话（用户提问、AI 回答、工具调用、工具返回结果）作为一个消息列表来管理。

**步骤 3: 定义图的节点与流程**
我们的对话“链”由三个核心节点和一个智能决策点组成：

1. **`query_or_respond` (决策节点)**：这是入口。LLM 在这里接收用户的最新消息和历史对话，然后决定是：

   * **调用 `retrieve` 工具**：如果问题需要查资料。
   * **直接回答**：如果问题是闲聊（如“你好”），则无需检索，直接生成回复。
2. **`tools` (工具执行节点)**：如果上一步决定调用工具，这个节点 (`ToolNode`) 负责实际执行 `retrieve` 工具，并将结果作为 `ToolMessage` 添加到状态中。
3. **`generate` (生成节点)**：此节点获取 `ToolMessage` 中的检索内容，结合原始问题和对话历史，生成最终的、有人情味的回答。

**流程图 (Control Flow):**
我们使用 `tools_condition` 这个条件边来创建智能流程：

* **入口** -> `query_or_respond`
* **`query_or_respond`** -> (如果调用了工具) -> **`tools`** -> **`generate`** -> **结束**
* **`query_or_respond`** -> (如果没调用工具) -> **结束** (直接短路)

```python
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

graph_builder = StateGraph(MessagesState) # 使用 MessagesState
graph_builder.add_node("query_or_respond", query_or_respond)
graph_builder.add_node("tools", ToolNode([retrieve]))
graph_builder.add_node("generate", generate)

graph_builder.set_entry_point("query_or_respond")
# 添加条件边，实现智能决策
graph_builder.add_conditional_edges("query_or_respond", tools_condition, {END: END, "tools": "tools"})
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()
```

**步骤 4: 添加记忆 - 持久化聊天记录**
为了让对话能够跨越多次请求，我们需要一个“记忆体”。LangGraph 的 `checkpointer` 机制完美解决了这个问题。

* 我们可以在编译图时加入一个 `checkpointer` (例如，`MemorySaver` 用于内存存储)。
* 在调用图时，通过 `config` 传入一个唯一的 `thread_id` 来标识每一段独立的对话。

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
# 编译时加入 checkpointer
graph = graph_builder.compile(checkpointer=memory)

# 调用时传入 thread_id，LangGraph 会自动存取历史记录
config = {"configurable": {"thread_id": "对话ID-123"}}
graph.stream(..., config=config)
```

---

#### **三、 方法二：构建智能“代理” (Agent)**

这种方法赋予 LLM 更大的自主权。Agent 可以在一轮对话中**自行决定进行多次、迭代的检索**，直到它认为收集到了足够的信息来回答一个复杂问题。

**核心思想**：Agent 的工作模式是一个**循环 (Loop)**。LLM 做出决策 -> 调用工具 -> 观察结果 -> 再做出决策... 直到问题解决。

**步骤 1: 使用预构建的 ReAct Agent**
LangGraph 提供了 `create_react_agent` 快捷方式，可以一键创建一个具备 ReAct 思维模式的 Agent。

```python
from langgraph.prebuilt import create_react_agent

# 将 LLM 和我们的工具列表传进去即可
agent_executor = create_react_agent(llm, [retrieve], checkpointer=memory)
```

**步骤 2: 理解 Agent 的工作流程**
与上面的“链”不同，Agent 的图结构中存在一个**循环**：

* LLM 接收问题后，决定调用 `retrieve` 工具。
* 工具返回结果后，这些信息会**再次**被送回给 LLM。
* LLM 审视新信息，判断是否足够回答。如果不够（例如，问题包含多个子问题），它会**再次**调用工具进行新一轮的检索，直到所有信息都搜集完毕，最后才生成最终答案。

**Agent 的优势**：非常适合处理需要**多步推理和信息搜集**的复杂问题。例如：“请先告诉我什么是任务分解的标准方法，然后再帮我查找这个方法的常见扩展有哪些？” Agent 会自动分两步进行检索。

---

#### **四、 总结：Chains vs. Agents**

| 特性       | **对话式“链” (Chain)** | **智能“代理” (Agent)**             |
| :------- | :----------------- | :----------------------------- |
| **控制权**  | 开发者定义固定流程，LLM 辅助决策 | LLM 拥有高度自主权，决定执行步骤             |
| **检索次数** | 每轮对话通常只有一次         | 可根据需要进行**多次、迭代**的检索            |
| **可预测性** | **高**，流程固定，易于调试    | **低**，行为更灵活，但也更难预测             |
| **适用场景** | 标准的、流程化的问答机器人      | 复杂、需要多步推理和探索的问答任务              |
| **实现**   | 手动搭建图节点和条件边        | 使用 `create_react_agent` 等预构建工具 |