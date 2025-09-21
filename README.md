# Nya-Akashi-Workshop: AI Persona Project

<img src="./README.assets/Akashi_3.png" alt="Akashi_3.png" style="zoom:50%;" />

**项目状态:** `v0.1.2 - 核心人格微调尝试`
**基础模型:** `Qwen/Qwen1.5-1.8B-Chat`
**核心技术:** `PEFT (QLoRA)`
**当前成果:** 成功在Google Colab环境下，对1.8B模型进行参数高效微调，使其具备了“明石”的角色人格（Persona）。

---

## 📖 项目简介 (Project Overview)

“Nya-Akashi-Workshop”是一个旨在从零开始，构建一个具备特定角色人格、拥有专业领域知识、并能主动使用工具完成任务的AI智能体的开源项目。

目前已完成第一阶段的路线图：通过PEFT技术对开源大模型进行微调，使其具备了《碧蓝航线》中的角色“明石”的人格特质和对话风格。

（实际上目前模型采用的1.8b测试，所以效果很差，后续真的跑的时候采用Qwen-7B-Chat模型）

### 🗺️ 路线图 (Roadmap)

阶段一（已经基本完成代码）：角色人格微调 (Persona Fine-tuning)
基于Qwen1.8B-Chat模型，使用PEFT技术，在Google Colab环境下，对模型进行参数高效微调。
后续将采用Qwen-7B-Chat模型，进一步提升模型的对话质量和逻辑能力。

阶段二：填充记忆 (RAG)
集成LangChain框架。
构建关于《碧蓝航线》游戏内容的向量数据库，使明石能回答专业、精确的游戏知识问题。

阶段三：智能进化 (AI Agent)
基于ReAct等理论，为明石赋予使用外部工具（如计算器、搜索引擎、API）的能力，让她从“对话伙伴”进化为“智能助理”。

阶段四：赋予身体 (Deployment)
使用Gradio或FastAPI + 前端框架，为项目构建一个可交互的Web应用。
利用Docker进行容器化，实现便捷部署。
模型升级探索:
在具备更强计算资源的条件下，尝试在7B级别模型上进行微调，以获得更强的逻辑和生成能力。

### 目前可跑

将tuning1.8bv2放入colab环境中，直接运行`Akashi_tuning1.8bv2.ipynb`即可。

## 🤝 贡献与交流 (Contributing)
本项目为个人学习与探索项目，欢迎鞭策，暂时不接受PR。

