### **ChatHuggingFace 自定义模型配置笔记**

#### **一、 环境设置**

在使用 `langchain-huggingface` 加载自定义模型前，需要先完成环境配置。

**1. 配置凭证**
首先，需要从 Hugging Face 获取你的 API 密钥（Access Token），并将其设置为环境变量 `HUGGINGFACEHUB_API_TOKEN`。

```python
import getpass
import os

if not os.getenv("HUGGINGFACEHUB\_API\_TOKEN"):
os.environ\["HUGGINGFACEHUB\_API\_TOKEN"] = getpass.getpass("请输入您的 Hugging Face API 密钥: ")

````

**2. 安装相关包**
执行以下命令安装所有必需的 Python 库。
```bash
%pip install --upgrade --quiet langchain-huggingface text-generation transformers google-search-results numexpr langchainhub sentencepiece jinja2 bitsandbytes accelerate
````

*注意：安装或更新包后，可能需要重启内核才能生效。*

---

#### **二、 模型实例化**

有两种主要方式可以实例化一个自定义的 `ChatHuggingFace` 模型。

**1. 通过 `HuggingFaceEndpoint`**
此方法通过连接到一个指定的 Hugging Face 模型仓库（repo\_id）来实现。你可以指定任务类型和推理服务提供商。

```python
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# 实例化 LLM 端点
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1-0528", # 指定模型仓库 ID
    task="text-generation",                  # 定义任务类型
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
    provider="auto",  # 由 Hugging Face 自动选择最佳服务提供商
)

# 将 LLM 封装为聊天模型
chat_model = ChatHuggingFace(llm=llm)
```

你也可以手动指定第三方推理服务提供商，例如 `hyperbolic`、`nebius` 或 `together`。

**2. 通过 `HuggingFacePipeline` (本地加载)**
此方法通常用于在本地环境中直接加载并运行模型。它会下载指定的模型文件到本地。

```python
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

# 通过模型 ID 直接加载
llm = HuggingFacePipeline.from_model_id(
    model_id="HuggingFaceH4/zephyr-7b-beta", # 指定要下载并加载的模型 ID
    task="text-generation",
    pipeline_kwargs=dict(
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    ),
)

# 封装为聊天模型
chat_model = ChatHuggingFace(llm=llm)
```

---

#### **三、 高级配置：量化加载模型**

为了在显存有限的设备上运行大模型，可以使用 `bitsandbytes` 进行量化。

1. **定义量化配置**
   创建一个 `BitsAndBytesConfig` 对象来指定量化参数（例如，以 4-bit 加载）。

   ```python
   from transformers import BitsAndBytesConfig

   quantization_config = BitsAndBytesConfig(
       load_in_4bit=True,
       bnb_4bit_quant_type="nf4",
       bnb_4bit_compute_dtype="float16",
       bnb_4bit_use_double_quant=True,
   )
   ```

2. **在 `HuggingFacePipeline` 中应用配置**
   在实例化 `HuggingFacePipeline` 时，通过 `model_kwargs` 参数传入量化配置。

   ```python
   llm = HuggingFacePipeline.from_model_id(
       model_id="HuggingFaceH4/zephyr-7b-beta",
       task="text-generation",
       pipeline_kwargs=dict(
           max_new_tokens=512,
           do_sample=False,
           repetition_penalty=1.03,
           return_full_text=False,
       ),
       model_kwargs={"quantization_config": quantization_config}, # 应用量化配置
   )

   chat_model = ChatHuggingFace(llm=llm)
   ```

---

#### **四、 模型调用**

实例化模型后，可以通过 `invoke` 方法与模型进行交互。

```python
from langchain_core.messages import HumanMessage, SystemMessage

# 构建消息列表（可以包含系统提示和用户输入）
messages = [
    SystemMessage(content="You're a helpful assistant"),
    HumanMessage(content="What happens when an unstoppable force meets an immovable object?"),
]

# 调用模型并获取回复
ai_msg = chat_model.invoke(messages)

# 打印模型生成的内容
print(ai_msg.content)
```