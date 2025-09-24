### **构建聊天机器人 (Chatbot) 核心笔记**

本笔记将引导您使用 LangChain 和 LangGraph 构建一个功能完善、带记忆的聊天机器人。

#### **一、 核心原理：让机器人拥有“记忆”**

1. **核心问题**：大语言模型 (LLM) 本身是**无状态的 (Stateless)**。这意味着，如果您不主动告诉它，它完全不记得之前的对话内容。
2. **解决方案**：在每次向 LLM 提问时，将**完整的对话历史 (Conversation History)** 作为下一次提问的上下文，一起发送给 LLM。这样，它就能“记起”之前聊过什么了。

---

#### **二、 使用 LangGraph 构建带记忆的聊天机器人**

LangGraph 的持久化机制 (`checkpointer`) 是实现聊天机器人记忆的现代化、推荐方案。

**步骤 1: 定义图和节点 (Define Graph and Node)**
我们先创建一个最简单的图，它只有一个节点，负责调用 LLM。

* **状态 (State)**：使用 LangGraph 内置的 `MessagesState`，它专门用于存储消息列表。
* **节点 (Node)**：创建一个 `call_model` 函数，它接收当前的状态（即所有消息），调用 LLM，然后返回新的消息。

```python
from langgraph.graph import START, MessagesState, StateGraph

# 定义一个新的图，其状态是 MessagesState
workflow = StateGraph(state_schema=MessagesState)

# 定义调用模型的节点函数
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # 返回的新消息会被自动追加到状态中
    return {"messages": response}

# 将节点添加到图中，并设置为起始节点
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
```

**步骤 2: 添加记忆持久化 (Add Memory/Persistence)**
这是实现“记忆”的关键！我们通过在编译图时添加一个 `checkpointer` 来实现。

* **`MemorySaver`**: 一个简单的内存检查点，用于存储对话历史。
* `checkpointer`: 它就像机器人的“记忆中枢”，自动保存和加载每个对话线程的状态。

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
# 编译图时，将 checkpointer 注入
app = workflow.compile(checkpointer=memory)
```

**步骤 3: 实现多用户对话 (Handle Multiple Users)**
通过在调用时传入一个 `config` 对象，并指定唯一的 `thread_id`，我们就能区分不同用户或不同轮次的对话。这就像是为每个不同的聊天窗口分配一个专属的“档案编号”。

```python
# 为这个对话线程指定一个唯一的 ID
config = {"configurable": {"thread_id": "user_001_session_A"}}

# 第一次调用
app.invoke({"messages": [HumanMessage("你好！我叫 Bob。")]}, config)

# 第二次调用，LangGraph 会自动加载这个 ID 的历史记录
app.invoke({"messages": [HumanMessage("我叫什么名字？")]}, config)
```

---

#### **三、 定制个性：使用提示模板 (Prompt Templates)**

为了让机器人有特定的角色或行为（比如像个海盗一样说话），我们可以使用 `ChatPromptTemplate`。

* **`system` 消息**: 在这里定义机器人的系统级指令。
* **`MessagesPlaceholder`**: 这是一个占位符，用于在 Prompt 中插入完整的对话历史。

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你说话的语气像个海盗。请尽你所能回答所有问题。"),
    MessagesPlaceholder(variable_name="messages"), # 告诉模板在这里插入历史消息
])

# 在 call_model 函数中，先用模板格式化输入，再调用 LLM
def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}
```

---

#### **四、 管理对话历史：防止“记忆”溢出**

如果对话一直持续，历史消息会无限增长，最终会超出 LLM 的上下文窗口限制。因此，我们需要一个机制来“修剪”历史记录。

* **`trim_messages`**: LangChain 提供的一个工具函数，可以根据设定的最大 token 数量来裁剪消息列表。
* **关键位置**: **加载历史记录之后，送入 Prompt 之前**。

```python
from langchain_core.messages import trim_messages

# 创建一个修剪器
trimmer = trim_messages(
    max_tokens=65,             # 允许的最大 token 数
    strategy="last",           # 保留最新的消息
    token_counter=model,       # 使用模型自身的分词器来计算 token
    include_system=True,       # 总是保留系统消息
)

# 在 call_model 函数中，调用 LLM 之前，先修剪消息
def call_model(state: State):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke({"messages": trimmed_messages, ...})
    response = model.invoke(prompt)
    return {"messages": [response]}
```

---

#### **五、 提升体验：流式输出 (Streaming)**

为了避免用户在等待 LLM 生成完整回答时的漫长空白，我们可以让机器人一个字一个字地“吐”出回答。

在 LangGraph 中实现这个非常简单，只需在调用 `.stream()` 方法时，指定 `stream_mode="messages"`。

```python
# stream_mode="messages" 会将最终的 AI Message 分解成 token 流
for chunk in app.stream(
    {"messages": [HumanMessage("你好，给我讲个笑话吧。")]},
    config,
    stream_mode="messages",
):
    print(chunk.content, end="|") # 实时打印每个 token
```