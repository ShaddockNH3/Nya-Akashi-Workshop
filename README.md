# Study

本study的基础是西二考核第七轮的一些本人在设计学习路线时的学习资料和一些个人的理解

是的，我也在学习中

## 参考资料

### **“Nya-Akashi-Workshop”技术栈与学习路径笔记**

**文档版本：** Nya-Akashi-Workshop
**核心目标：** 构建一个具备特定角色（Persona）、专业知识库和工具使用能力的AI智能体。

---

#### **阶段一：注入灵魂 —— 大模型微调 (Fine-tuning)**

**目标：** 使预训练模型学习并模仿“明石”的角色特征，包括语言风格、口癖及性格。

* **核心理论与工具：Hugging Face 生态**

  * **圣经级教程 (必修):** [Hugging Face 官方NLP课程 (中文版)](https://huggingface.co/learn/nlp-course/zh-CN/chapter1/1)

    * **内容解析：** 系统性地讲解了`transformers`库的使用，涵盖从数据预处理、模型加载、到训练与评估的全流程。是进行任何微调工作的理论基石。
  * **参数高效微调 (PEFT) 理论:**

    * **官方文档:** [Hugging Face PEFT 库文档](https://huggingface.co/docs/peft/index) - PEFT库的权威指南，详细介绍了LoRA等多种方法的原理和API。
    * **深度解读:** [LLM Tuning Techniques by Sebastian Raschka](https://magazine.sebastianraschka.com/p/finetuning-llms) - 一篇高质量的技术博客，深入浅出地解释了LoRA的工作原理及其在LLM微调中的优势。
    * **学习价值：** 理解为何LoRA能够以极低的资源成本实现高效微调，是选择此技术路径的理论依据。

* **实战演练 (Hands-on Practice):**

  * **一站式图形化工具 (推荐新手):** [LLaMA Factory GitHub 项目](https://github.com/hiyouga/LLaMA-Factory)

    * **功能解析：** 集成了多种主流LLM（如Qwen, Llama）和PEFT微调方法（如LoRA），提供图形化界面（WebUI）。用户无需编写大量代码即可完成微调任务，极大地降低了入门门槛，是快速验证数据和想法的利器。
  * **代码级底层实现:** [动手学深度学习 - 微调BERT](https://zh-v2.d2l.ai/chapter_natural-language-processing-applications/finetuning-bert.html)

    * **学习价值：** 通过经典的BERT微调案例，深入理解微调过程中的数据处理、模型结构修改以及训练循环的底层代码逻辑。有助于在脱离高级封装（如`SFTTrainer`）后，仍具备自定义训练流程的能力。

---

#### **阶段二：填充记忆 —— RAG 知识库 (Retrieval-Augmented Generation)**

**目标：** 使模型能够访问并利用外部知识（如碧蓝航线游戏资料），回答其预训练数据中不包含的、特定领域的问题。

* **核心框架 (二选一深入):**

  * **LangChain (瑞士军刀):** [LangChain 官方文档 (Python)](https://python.langchain.com/docs/get_started/introduction)

    * **定位分析：** 一个功能全面的LLM应用开发框架，覆盖数据连接、模型交互、链式调用、Agent构建等多个方面。RAG是其核心功能之一。推荐从`Quickstart`入手，理解其“链(Chain)”的核心概念。
  * **LlamaIndex (专业选手):** [LlamaIndex 官方文档](https://docs.llamaindex.ai/en/stable/)

    * **定位分析：** 专注于为RAG构建优化的数据索引和查询流程。对于需要处理大量、复杂文档的RAG应用，其数据处理和索引能力通常更胜一筹。

* **RAG关键组件：**

  * **向量数据库 (Vector Database):**

    * **概念入门:** [什么是向量数据库? (YouTube 视频)](https://www.youtube.com/watch?v=S2ro_C0p_3k) - 通过可视化方式理解其核心功能：存储文本的向量表示（Embeddings），并进行高效的相似度搜索。
  * **嵌入模型 (Embedding Model):**

    * **模型选型:** [BGE Embedding 模型主页](https://huggingface.co/BAAI/bge-large-zh-v1.5) - 一个性能优异的中文嵌入模型，负责将文本块转换为高维向量。其主页提供了加载和使用的标准代码片段。
  * **端到端实战教程:** [Chat with Documents using LangChain (YouTube 视频)](https://www.youtube.com/watch?v=2xxziIWmaSA) - 一个经典的RAG实现教程，完整演示了从加载文档、切分、生成嵌入、存入向量数据库、到构建检索链进行问答的全过程。

---

#### **阶段三：智能进化 —— Agent 智能体 (AI Agent)**

**目标：** 使模型从一个被动的问答机器人，进化为能够主动规划、调用外部工具（如搜索引擎、计算器）来完成复杂任务的智能助理。

* **核心理论：ReAct (Reasoning and Acting)**

  * **经典入门读物:** [Lilian Weng - LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) - OpenAI研究员撰写的综述性文章，系统性地梳理了LLM Agent的核心思想、架构和主流方法（如ReAct）。
  * **溯源文献:** [ReAct 论文 (arXiv)](https://arxiv.org/abs/2210.03629) - 提出了“思考-行动-观察”循环的ReAct框架的原始论文，是理解现代Agent行为模式的基础。

* **实战演练：**

  * **LangChain Agent 实现:** [LangChain - Agents 官方文档](https://python.langchain.com/docs/modules/agents/) - LangChain关于Agent模块的权威文档，详细讲解了如何定义工具（Tools）、初始化Agent Executor以及Agent的决策循环。是构建Agent最主要的实践参考。
  * **视频指导:** [LangChain Agents Tutorial (YouTube 视频)](https://www.youtube.com/watch?v=n_KT-Iu_c2c) - 手把手教学，演示如何使用LangChain创建一个可以调用API（如搜索引擎）来回答问题的简单Agent。

---

#### **阶段四：赋予身体 —— 应用部署 (Deployment)**

**目标：** 将后台的AI能力封装成一个可交互的应用，供最终用户使用。

* **前端快速原型:**

  * **Gradio:** [Gradio 官方文档](https://www.gradio.app/guides/quickstart) - 一个能够用极简Python代码快速生成Web交互界面的库，非常适合快速搭建聊天机器人的演示Demo。
* **专业后端服务:**

  * **FastAPI:** [FastAPI 官方文档 (中文)](https://fastapi.tiangolo.com/zh/tutorial/) - 一个现代化、高性能的Python Web框架，用于构建API接口。其文档清晰易懂，是构建稳定、可扩展AI后端的首选。
* **容器化与分发:**

  * **Docker:** [Docker Get Started](https://docs.docker.com/get-started/) - 学习使用Docker将整个应用（包括代码、依赖、环境配置）打包成一个标准的“容器镜像”，实现“一次构建，处处运行”，极大简化了部署流程。