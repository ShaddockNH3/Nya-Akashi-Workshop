### **构建语义搜索引擎全流程笔记**

本笔记将引导您使用 LangChain 构建一个完整的语义搜索引擎，核心流程包括：**加载文档 -> 分割文本 -> 创建嵌入 -> 存入向量库 -> 进行检索**。

#### **一、 核心概念**

在开始之前，我们需要了解几个关键概念：

* **文档 (Documents) 与文档加载器 (Document Loaders)**：将外部数据（如PDF、网页）加载为程序可处理的统一格式。
* **文本分割器 (Text Splitters)**：将长文档切分成更小的、语义完整的块，以便于嵌入和检索。
* **嵌入 (Embeddings)**：将文本块转换为数值向量（Vector）的过程。语义相似的文本在向量空间中的距离也相近。
* **向量存储 (Vector Stores) 与检索器 (Retrievers)**：专门用于存储文本向量并提供高效相似度搜索功能的数据库，而检索器则是执行这些搜索任务的标准化接口。

---

#### **二、 环境设置**

**1. 安装必要库**
首先，确保您已经安装了 LangChain 的核心组件和 PDF 解析库 `pypdf`。

```bash
pip install langchain-community pypdf
```

**2. (可选) 配置 LangSmith**
LangSmith 是一个用于调试、追踪和评估 LangChain 应用的强大工具。如果需要，可以设置环境变量来启用它。

```python
import getpass
import os

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("请输入您的 LangSmith API Key: ")
```

---

#### **三、 步骤一：文档加载 (Documents and Document Loaders)**

所有数据处理的第一步都是加载数据。LangChain 的 `Document` 对象是标准的数据单元，它包含 `page_content` (文本内容) 和 `metadata` (元数据，如来源、页码等)。

我们将使用 `PyPDFLoader` 来加载一个 PDF 文件，它会把 PDF 的每一页都转换成一个独立的 `Document` 对象。

```python
from langchain_community.document_loaders import PyPDFLoader

# 假设 PDF 文件路径
file_path = "../example_data/nke-10k-2023.pdf"

# 实例化加载器并加载文档
loader = PyPDFLoader(file_path)
docs = loader.load()

# 查看加载的页面总数
print(f"PDF 总共加载了 {len(docs)} 页内容。")

# 查看第一页的内容和元数据
print(f"第一页前200个字符预览: \n{docs.page_content[:200]}")
print(f"第一页的元数据: \n{docs.metadata}")
```

---

#### **四、 步骤二：文本分割 (Splitting)**

直接对整页进行嵌入和搜索效果不佳，因为单页内容太多，主题可能分散。我们需要将每一页进一步分割成更小的文本块（chunks）。

这里我们使用 `RecursiveCharacterTextSplitter`，它会智能地按段落、换行符等进行分割，以保证语义的连贯性。

* `chunk_size`: 每个文本块的最大字符数。
* `chunk_overlap`: 块与块之间的重叠字符数，以防止切断完整的句子。
* `add_start_index`: 在元数据中记录每个块在原文中的起始位置。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 定义文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # 每个块的大小为 1000 个字符
    chunk_overlap=200,     # 相邻块之间重叠 200 个字符
    add_start_index=True   # 记录每个块的起始索引
)

# 对所有加载的页面进行分割
all_splits = text_splitter.split_documents(docs)

print(f"所有文档被分割成了 {len(all_splits)} 个小块。")
```

---

#### **五、 步骤三：文本嵌入 (Embeddings)**

为了让计算机理解文本的语义，我们需要将分割好的文本块转换为向量。这个过程就是“嵌入”。LangChain 支持多种嵌入模型，这里我们以 OpenAI 的模型为例。

**1. 安装并配置 OpenAI**

```
pip install -qU langchain-openai
```

```python
import getpass
import os

# 确保设置了 OpenAI API Key
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("请输入您的 OpenAI API Key: ")
```

**2. 创建嵌入模型实例**

```python
from langchain_openai import OpenAIEmbeddings

# 实例化嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 示例：将一个文本块转换为向量
vector = embeddings.embed_query(all_splits.page_content)
print(f"生成的向量维度为: {len(vector)}")
print(f"向量的前10个值: \n{vector[:10]}")
```

---

#### **六、 步骤四：向量存储 (Vector Stores)**

向量存储是一个专门的数据库，用于高效地存储并搜索大量的向量。我们将分割好的文本块进行嵌入，然后存入向量库中建立索引。

这里我们使用一个轻量级的内存向量库 `InMemoryVectorStore` 作为演示。

```python
from langchain_core.vectorstores import InMemoryVectorStore

# 使用指定的嵌入模型初始化向量库
vector_store = InMemoryVectorStore(embeddings)

# 将所有分割好的文本块（及其向量）添加到向量库中
ids = vector_store.add_documents(documents=all_splits)
```

**进行相似度搜索**
索引建立好后，就可以用自然语言进行查询了。向量库会自动将你的查询语句转换为向量，并在库中寻找与之最相似的文本块。

```python
# 示例查询
query = "How many distribution centers does Nike have in the US?"

# 执行相似度搜索
results = vector_store.similarity_search(query)

# 打印最相关的结果
print(results.page_content)
```

向量库还支持多种搜索方式，例如：
*   `asimilarity_search`: 异步搜索。
*   `similarity_search_with_score`: 返回结果的同时，还返回相似度得分。
*   `similarity_search_by_vector`: 直接使用一个向量进行搜索。

---

#### **七、 步骤五：检索器 (Retrievers)**

检索器 (Retriever) 是一个比向量库更高层次的抽象，它被设计为标准的 `Runnable` 接口，可以更方便地融入到 LangChain 的调用链 (Chains) 中。

我们可以很轻松地从一个向量库创建一个检索器。

```python
# 将向量库转换为一个检索器
# search_kwargs={"k": 1} 表示每次只返回最相关的 1 个结果
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
)

# 使用检索器进行批量查询
queries = [
    "How many distribution centers does Nike have in the US?",
    "When was Nike incorporated?",
]
batch_results = retriever.batch(queries)

# 打印批量查询的结果
for result in batch_results:
    print(result.page_content)
    print("-" * 20)
````

检索器支持不同的搜索类型，如 `"mmr"` (最大边际相关性，用于增加结果的多样性) 和 `"similarity_score_threshold"` (根据相似度得分进行过滤)。
