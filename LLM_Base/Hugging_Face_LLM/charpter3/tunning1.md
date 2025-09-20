## 数据集处理与准备

本章阐述了为模型微调（Fine-tuning）准备和处理数据集的完整流程。核心内容包括从 Hugging Face Hub 加载数据集、使用 Tokenizer 进行预处理、以及通过动态填充（Dynamic Padding）高效地构建批处理（batch）。

#### 1. 模型训练的基本逻辑

在 `transformers` 库中，模型训练流程需要将标签（labels）直接包含在模型输入中。模型在接收到带有 `labels` 的批处理数据后，会自动计算损失（Loss）。一个简化的训练步骤如下：

```python
# 伪代码：单步训练的基本原理
batch = tokenizer(sequences, padding=True, return_tensors="pt")
batch["labels"] = torch.tensor([1, 1])  # 添加对应的标签

optimizer = AdamW(model.parameters())
loss = model(**batch).loss  # 模型自动计算损失
loss.backward()             # 反向传播
optimizer.step()            # 更新权重
```

#### 2. 从 Hub 加载数据集

Hugging Face `datasets` 库提供了对 Hub 上数千个数据集的便捷访问。

* **加载命令:**
  使用 `load_dataset` 函数可以下载并缓存指定的数据集。该函数可以接受多个参数，例如数据集名称和子集名称。

  ```python
  from datasets import load_dataset

  # 加载 GLUE 基准测试中的 MRPC 数据集
  raw_datasets = load_dataset("glue", "mrpc") 
  ```

* **数据集结构:**
  加载后通常得到一个 `DatasetDict` 对象，它是一个类字典结构，包含了训练（train）、验证（validation）和测试（test）等不同的数据分割。

  ```
  DatasetDict({
      train: Dataset({...}),
      validation: Dataset({...}),
      test: Dataset({...})
  })
  ```

  每个 `Dataset` 对象都包含了数据集的特征（features）和样本行数（num\_rows）。可以通过索引或字典键来访问具体的数据子集和样本。

* **特征查看:**
  数据集的 `features` 属性记录了每一列的数据类型，对于分类任务，`ClassLabel` 类型会明确指出标签索引与实际类别名称的映射关系。

  ```python
  raw_datasets["train"].features["label"]
  # ClassLabel(num_classes=2, names=['not_equivalent', 'equivalent'], ...)
  ```

#### 3. 数据集预处理

预处理的核心是将文本数据转换为模型可用的 `input_ids`, `attention_mask` 等张量。

* **处理句子对:**
  对于需要输入两个句子的任务（如句子对分类），Tokenizer 可以直接接收两个句子列表作为输入。它会自动按照模型预训练时的方式（如 `[CLS] sentence1 [SEP] sentence2 [SEP]`）来组织 `input_ids`。同时，会生成 `token_type_ids` 来区分两个句子。`token_type_ids` 的作用是指示模型输入的哪个部分属于第一个句子（通常为 `0`），哪个部分属于第二个句子（通常为 `1`）。

  ```python
  # Tokenizer 能够直接处理成对的句子
  inputs = tokenizer("This is the first sentence.", "This is the second one.")
  # inputs 字典将包含 input_ids, token_type_ids, 和 attention_mask
  ```

* **使用 `map` 方法进行高效处理:**
  直接对整个数据集进行 Tokenization 可能会消耗大量内存。`datasets` 库推荐使用 `Dataset.map()` 方法，它能够高效地对数据集的每个样本应用一个预处理函数。

  1. **定义处理函数:** 创建一个函数，接收一个样本（`example`），并返回经过 Tokenizer 处理后的结果。

     ```python
     def tokenize_function(example):
         return tokenizer(example["sentence1"], example["sentence2"], truncation=True)
     ```
  2. **应用 `map`:** 调用 `map()` 方法，并将 `batched=True` 参数设为 `True`。这使得函数可以一次性处理多个样本，极大地提升了处理速度，尤其是在使用由 Rust 编写的 "fast" Tokenizer 时。

     ```python
     tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
     ```

  `map` 方法会将处理函数返回字典中的新键（如 `input_ids`）作为新列添加到原数据集中。

#### 4. 动态填充 (Dynamic Padding)

在预处理时，推荐不在 `map` 阶段进行全局填充（即不设置 `padding` 参数）。全局填充会将所有样本都填充到整个数据集的最大长度，造成计算资源的浪费。更优的策略是 **动态填充**。

* **定义:** 动态填充是指在构建每个批处理（batch）时，仅将该批次内的样本填充到当前批次中最长样本的长度。

* **实现方式:**
  通过 `DataCollatorWithPadding` 实现。`DataCollator` 是一个在构建 `DataLoader` 时用于整理批处理数据的函数。`DataCollatorWithPadding` 接收一个 `tokenizer` 实例，并能自动地对批处理中的 `input_ids`, `attention_mask` 等进行正确的动态填充。

  ```python
  from transformers import DataCollatorWithPadding

  data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
  ```

* **验证:**
  从数据集中取出小批量样本，应用 `data_collator`。可以观察到，输出的批处理张量具有统一的维度，其长度等于该批次中原始样本的最大长度。

  ```python
  samples = tokenized_datasets["train"][:8]
  samples = {k: v for k, v in samples.items() if k not in ["idx", "sentence1", "sentence2"]}
  batch = data_collator(samples)
  # batch 中所有张量的序列长度维度都将是统一的
  ```

通过以上流程，数据集被高效地转换为模型微调所需的、经过动态填充的批处理格式，为接下来的训练步骤做好了准备。