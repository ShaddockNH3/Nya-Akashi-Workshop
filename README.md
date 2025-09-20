# Study

本study的基础是结束西二AI考核的所有内容。

## 基础学习

参考资料

1. [Hugging Face 官方课程 (中文)](https://huggingface.co/learn/nlp-course/zh-CN/chapter1/1)





---

乱七八糟

emmm，如果你觉得不好用，还有其他的框架可以看一看。但不管是你手搓还是用框架，重点是需要解决这几个问题。
1. 幻觉问题，用户问到回答不了的需要回答不知道。
2.敏感词或者不合法的提问要拒绝回答
3. 输出要检验
然后就是我去看了一下nemo guardrails。我自己认为哈，还是可以用的。改动肯定是有，但目前项目已经很简单了，naiverag几乎是五分钟就能重写出来的程度。
首先，你说的不支持模型，你可以查一查custom_llm，你可以看一看仓库里的vllm_llm，那里就是我自定义的langchain的llm。而这个guardrails框架自定义的llm就是去继承langchain的LLM类。简而言之，我之前已经完成过，可以直接用。https://docs.nvidia.com/nemo/guardrails/latest/user-guides/configuration-guide.html
其次，可以和langchain集成，从这个角度也很容易嵌入进入https://github.com/NVIDIA/NeMo-Guardrails/tree/develop/docs/user-guides/langchain/chain-with-guardrails
最后，他有一个demo，而且比我们的复杂的多，可以看看他的config.py是怎么写的，工具、LLM怎么注册之类的。https://github.com/NVIDIA/NeMo-Guardrails/tree/develop/examples/configs/rag/multi_kb
最后就是，如果不用这个框架，你需要找一个同样解决问题的框架，并且使用上

另一个框架guardrails ai有一个示例。https://www.guardrailsai.com/blog/reduce-ai-hallucinations-provenance-guardrails

具体的大模型应用安全风险可以看一下这个https://owasp.org/www-project-top-10-for-large-language-model-applications/



* **PyTorch 深度学习框架:**

  * **藏宝图:** [PyTorch 官方 60 分钟入门教程](https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html) (有中文版) - 动手实践，快速了解 PyTorch 如何工作。
  * **为什么需要？** Hugging Face 的模型库就是基于 PyTorch 的，这是我们训练“明石”大脑的基础。

* **Git 与 GitHub:**

  * **藏宝图:** [Pro Git 中文版](https://git-scm.com/book/zh/v2) - 像一本字典，想查什么都有。或者 [猴子都能懂的 Git 入门](http://backlog.com/git-tutorial/cn/) - 超级可爱的图文教程！
  * **为什么需要？** 方便管理我们的代码，还能从 GitHub 上下载很多很棒的开源项目\~

---

#### 阶段一：注入灵魂！—— 大模型微调 (Fine-tuning)

这是让模型学会像明石一样说话的关键一步！

* **核心理论与工具 (Hugging Face):**

  * **藏宝图 1 (必看！):** [Hugging Face 官方课程 (中文)](https://huggingface.co/learn/nlp-course/zh-CN/chapter1/1) - 从头到尾，系统地教你如何使用 Transformers 库，是我们的“圣经”！
  * **藏宝图 2 (LoRA):** [Hugging Face PEFT 库文档](https://huggingface.co/docs/peft/index) 和这篇介绍 LoRA 的博客 [LLM-tuning-techniques](https://magazine.sebastianraschka.com/p/finetuning-llms)。
  * **为什么需要？** 让你明白什么是 LoRA，为什么它能让我们用较少的资源微调出好效果。

* **实战演练 (Hands-on Practice):**

  * **藏宝图 3 (一站式项目):** [LLaMA Factory GitHub 项目](https://github.com/hiyouga/LLaMA-Factory) - 一个集成了各种模型和微调方法的图形化界面工具，超级适合新手！你可以用它来微调 Qwen 或者 Llama 模型，几乎是点几下鼠标的事，强烈推荐从这里开始！
  * **藏宝图 4 (代码级教程):** [李沐·动手学深度学习 - 微调BERT](https://zh-v2.d2l.ai/chapter_natural-language-processing-applications/finetuning-bert.html) - 如果想深入代码细节，可以看看这个，了解微调的底层逻辑。

---

#### 阶段二：填充记忆！—— RAG 知识库 (Retrieval-Augmented Generation)

给明石装上碧蓝航线的“无敌小仓库”！

* **核心框架 (LangChain / LlamaIndex):**

  * **藏宝图 1 (LangChain):** [LangChain 官方文档 (Python)](https://python.langchain.com/docs/get_started/introduction) - 从这里开始，了解它的核心组件和工作流程。先看 `Quickstart` 部分。
  * **藏宝图 2 (LlamaIndex):** [LlamaIndex 官方文档](https://docs.llamaindex.ai/en/stable/) - 特别为 RAG 优化，它的 `Getting Started` 教程非常清晰。
  * **小贴士:** 两个框架选一个深入学习就好啦\~ LangChain 更像一个大而全的瑞士军刀，LlamaIndex 更专注于 RAG 这个核心功能。

* **向量数据库与嵌入模型:**

  * **藏宝图 3 (向量数据库概念):** [什么是向量数据库？(YouTube 视频)](https://www.youtube.com/watch?v=S2ro_C0p_3k) - 一个简单的视频，让你直观地理解它的作用。
  * **藏宝图 4 (嵌入模型):** [BGE Embedding 模型主页](https://huggingface.co/BAAI/bge-large-zh-v1.5) - 看看它的介绍，了解如何加载和使用它，很简单哦。
  * **藏宝图 5 (实战教程):** [Chat with Documents using LangChain (YouTube 视频)](https://www.youtube.com/watch?v=2xxziIWmaSA) - 一个非常经典的英文教程，完整地演示了如何用 LangChain 读取文档 -> 向量化 -> 存入数据库 -> 进行问答的全过程。

---

#### 阶段三：变得更聪明！—— Agent 智能体 (AI Agent)

让明石从“问答机”进化成“小助理”！

* **核心理论 (ReAct):**

  * **藏宝图 1 (必读博客):** [Lilian Weng - LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) - 这篇文章是 Agent 领域的经典入门读物，解释了 Agent 的核心思想和不同方法。
  * **藏宝图 2 (原版论文):** [ReAct 论文](https://arxiv.org/abs/2210.03629) - 如果想追本溯源，可以挑战一下原版论文喵\~

* **实战演练 (Building Agents):**

  * **藏宝图 3 (LangChain Agent):** [LangChain - Agents](https://python.langchain.com/docs/modules/agents/) - 官方文档详细介绍了如何创建 Agent、定义工具、以及 Agent 的工作流程。这是最重要的实践资料！
  * **藏宝图 4 (视频教程):** [LangChain Agents Tutorial (YouTube 视频)](https://www.youtube.com/watch?v=n_KT-Iu_c2c) - 手把手教你如何用 LangChain 创建一个会使用搜索工具的 Agent。

---

#### 阶段四：给她一个身体！—— 应用部署 (Deployment)

让大家都能和可爱的明石聊天\~

* **快速搭建界面:**

  * **藏宝图 1:** [Gradio 官方文档](https://www.gradio.app/guides/quickstart) - 你会惊讶于用它搭建一个聊天界面有多么简单！几行代码就搞定！

* **搭建专业后端:**

  * **藏宝图 2:** [FastAPI 官方文档](https://fastapi.tiangolo.com/zh/tutorial/) - 它的文档被誉为教程界的典范，跟着走一遍，你就能写出高性能的 API 了。

* **打包与分享:**

  * **藏宝图 3:** [Docker Get Started](https://docs.docker.com/get-started/) - 学习如何把你的应用打包成一个“魔法盒子”，在哪里都能运行。