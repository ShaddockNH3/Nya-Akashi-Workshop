### **构建智能代理 (Agent) 核心笔记**

Agent 是一个以 LLM 为**推理核心**的系统。它能自主地**决定**采取什么行动 (Action)、使用什么**工具 (Tool)**，并根据工具返回的结果**再次思考**，决定下一步是继续行动还是完成任务。

#### **一、 Agent 的核心工作流程 (ReAct 模式)**

Agent 的思考和行动遵循一个循环，通常被称为 **ReAct (Reasoning and Acting)** 模式：

1. **思考 (Reason)**：LLM 分析当前的用户请求和对话历史，判断用户的意图。
2. **决策 (Act)**：LLM 决定是否需要使用工具。如果需要，它会选择最合适的工具，并生成调用该工具所需的参数（例如，为搜索引擎生成查询关键词）。
3. **观察 (Observe)**：执行工具，并将返回的结果（例如，搜索结果）反馈给 LLM。
4. **再次思考**：LLM “观察”到工具返回的结果后，再次进行思考，判断信息是否足够回答用户问题。如果足够，就生成最终答案；如果不够，就回到第 2 步，可能会调用另一个工具或使用不同的参数再次调用工具。

---

#### **二、 构建 Agent 的三大核心组件**

1. **大语言模型 (LLM)**：担当 Agent 的“**大脑**”，负责推理、决策和生成回答。
2. **工具 (Tools)**：Agent 的“**工具箱**”或“**双手**”，定义了 Agent 能执行的具体操作。例如，网络搜索、数据库查询、代码执行等。
3. **Agent 执行器 (Agent Executor)**：这是驱动 Agent 运行的“**引擎**”，它负责协调 LLM 和 Tools 之间的 ReAct 循环。在 LangGraph 中，`create_react_agent` 就是一个强大而便捷的执行器构造器。

---

#### **三、 详细步骤：构建一个会搜索的聊天 Agent**

**步骤 1: 定义工具 (Define Tools)**
首先，我们要为 Agent 配备它能使用的工具。这里我们使用 `TavilySearch` 作为一个强大的网络搜索工具。

```python
from langchain_tavily import TavilySearch

# 实例化一个搜索工具，max_results=2 表示每次最多返回 2 条搜索结果
search = TavilySearch(max_results=2)

# 将所有工具放入一个列表中
tools = [search]
```

*您可以定义任意多个自定义工具，只要将它们都放入 `tools` 列表即可。*

**步骤 2: 准备大语言模型 (Prepare the LLM)**
LLM 需要“知道”自己有哪些工具可以用。我们通过 `.bind_tools()` 方法将工具列表“绑定”到模型上。

```python
# 假设 model 已经初始化
# 将工具信息绑定到模型上，让模型具备调用这些工具的能力
model_with_tools = model.bind_tools(tools)
```

绑定后，当 LLM 接收到需要外部信息才能回答的问题时（例如“旧金山今天天气怎么样？”），它的输出就不再是纯文本，而是一个包含 `tool_calls` 的特殊消息，指示执行器去调用某个工具。

**步骤 3: 一键创建 Agent 执行器 (Create the Agent Executor)**
LangGraph 提供了 `create_react_agent` 这个高级函数，它将 LLM、工具和 ReAct 循环逻辑完美地封装在一起，我们只需一行代码就能创建一个功能完备的 Agent。

```python
from langgraph.prebuilt import create_react_agent

# 传入原始的 model (函数内部会自动绑定工具) 和工具列表
agent_executor = create_react_agent(model, tools)
```

**步骤 4: 添加记忆 (Adding Memory)**
和构建聊天机器人一样，我们通过 `checkpointer` 来为 Agent 赋予跨轮次的对话记忆。

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# 在创建时传入 checkpointer
agent_executor = create_react_agent(model, tools, checkpointer=memory)
```

*这样，Agent 不仅能执行任务，还能记住之前的对话内容，例如记住用户的名字和居住地。*

**步骤 5: 运行并与 Agent 交互**
调用 Agent 时，同样需要传入 `thread_id` 来管理对话状态。

```python
# 为对话指定一个线程 ID
config = {"configurable": {"thread_id": "user_pro_session_007"}}

# 第一轮对话：自我介绍
input_1 = {"messages": [("user", "你好！我叫 Bob，住在旧金山。")]}
agent_executor.invoke(input_1, config)

# 第二轮对话：提问，Agent 会利用记忆和工具来回答
input_2 = {"messages": [("user", "我住的地方天气怎么样？")]}
# Agent 会思考：“我”住在哪里 -> 从记忆中找到“旧金山” -> 决策：使用搜索工具 -> 生成查询“旧金山天气” -> 执行搜索 -> 观察结果 -> 生成答案
agent_executor.invoke(input_2, config)
```

**步骤 6: 流式输出 (Streaming)**
为了获得更好的交互体验，我们可以流式地观察 Agent 的每一步思考和行动。

* `stream_mode="values"`: 流式返回每一步（思考、工具调用、工具结果、最终回答）完整的消息。
* `stream_mode="messages"`: 当 Agent 最终生成回答时，可以流式返回每一个 token。

```python
# 流式观察 Agent 的每一步行动
for step in agent_executor.stream(input_2, config, stream_mode="values"):
    step["messages"][-1].pretty_print()
```