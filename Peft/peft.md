## peft

由于没有本地显卡，是在colab上跑的，因此传统的模型微调肯定是没办法跑的。

所以引出[peft](https://huggingface.co/docs/peft/quicktour)，其中有一个技术是LoRA（Low-Rank Adaptation），可以不进行真的微调，只是为模型穿上一层“外骨骼”，大大降低训练成本。

#### **一、 核心思想与目标**

* **问题陈述 (Problem Statement):**
  对大规模预训练语言模型（Large Language Models, LLMs）进行全参数微调（Full Fine-Tuning）在计算资源和存储上成本极高，不具备可扩展性。

* **PEFT 解决方案 (Solution):**
  提出参数高效微调方法，通过冻结预训练模型绝大部分参数，仅训练一小部分新增的或指定的参数。其优势在于：

  1. **降低计算成本:** 大幅减少训练过程中所需的GPU显存和计算量。
  2. **降低存储成本:** 微调后仅需存储少量新增参数（适配器），而非整个模型的副本，通常仅占原模型大小的极小部分（如\~0.2%）。
  3. **避免灾难性遗忘 (Catastrophic Forgetting):** 由于不改动原模型参数，模型在预训练阶段学到的通用能力得以保留。
  4. **便携性与模块化:** 不同的任务对应不同的适配器，可以轻松切换，实现一个基础模型服务于多个下游任务。

* **主流方法:**

  * **LoRA (Low-Rank Adaptation):** 通过在模型的特定层（通常是Attention层）中注入低秩矩阵分解（`A`和`B`矩阵）来模拟参数更新，训练的正是这些低秩矩阵。
  * **Prompt Tuning:** 冻结整个模型，仅训练添加到输入前的少量“软提示”（Soft Prompts）参数。

#### **二、 PEFT (LoRA) 训练流程详解**

##### **1. 配置 (Configuration) - `LoraConfig`**

训练开始前，必须定义一个`LoraConfig`对象来指定LoRA的超参数，它是构建`PeftModel`的基础。

* **关键参数:**

  * `task_type`: 任务类型。对于自回归模型（如GPT系列、Qwen），应设为 `TaskType.CAUSAL_LM`。对于编码器-解码器模型（如T5），则为 `TaskType.SEQ_2_SEQ_LM`。
  * `inference_mode`: 布尔值，指定当前配置是用于训练 (`False`) 还是推理 (`True`)。
  * `r`: **LoRA的秩 (Rank)**。这是最核心的参数之一，定义了低秩分解矩阵的维度。`r` 值越大，可训练参数越多，模型的拟合能力越强，但计算和存储开销也相应增加。通常选择8, 16, 32等值作为起点。
  * `lora_alpha`: **LoRA的缩放因子 (Scaling Factor)**。LoRA的输出会乘以一个 `alpha/r` 的缩放系数。`alpha` 的作用是调整LoRA适配器对原模型输出的贡献权重。一个常见的经验法则是将 `alpha` 设置为 `r` 的两倍。
  * `lora_dropout`: LoRA层的Dropout概率。用于正则化，防止过拟合。
  * `target_modules`: 一个字符串列表，指定要应用LoRA的目标模块名称。对于Transformer模型，通常是Attention机制中的查询（`q_proj`）、键（`k_proj`）、值（`v_proj`）和输出（`o_proj`）投影层。

* **代码示例:**

  ```python
  from peft import LoraConfig, TaskType

  peft_config = LoraConfig(
      task_type=TaskType.CAUSAL_LM, 
      r=8, 
      lora_alpha=16, 
      lora_dropout=0.05,
      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
  )
  ```

##### **2. 模型封装 (Wrapping) - `get_peft_model`**

将基础的预训练模型与`LoraConfig`结合，生成一个可用于参数高效训练的`PeftModel`。

1. **加载基础模型:** 从`transformers`库加载预训练模型。

   ```python
   from transformers import AutoModelForCausalLM

   base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen1.5-1.8B-Chat")
   ```

2. **应用PEFT配置:** 使用`get_peft_model`函数进行封装。该函数会冻结基础模型的所有参数，并根据`LoraConfig`在指定的目标模块中添加可训练的LoRA层。

   ```python
   from peft import get_peft_model

   model = get_peft_model(base_model, peft_config)
   ```

3. **验证可训练参数:** 调用`print_trainable_parameters()`方法，可以清晰地看到可训练参数的数量、总参数量以及二者的比例。这是验证PEFT配置是否成功应用的关键步骤。

   ```python
   model.print_trainable_parameters()
   # output: trainable params: 4,718,592 || all params: 1,836,093,440 || trainable%: 0.2570
   ```

##### **3. 训练 (Training) - `transformers.Trainer`**

生成的`PeftModel`对象与标准的`transformers`模型完全兼容，可以直接传入`Trainer`类进行训练。

* **流程:**

  1. 定义`TrainingArguments`，设置输出目录、学习率、批大小、训练轮次等训练超参数。
  2. 实例化`Trainer`，传入`PeftModel`、训练参数、数据集、分词器等组件。
  3. 调用`trainer.train()`启动训练。

* **代码示例:**

  ```python
  from transformers import TrainingArguments, Trainer

  training_args = TrainingArguments(
      output_dir="path/to/output",
      num_train_epochs=3,
      per_device_train_batch_size=4,
      learning_rate=2e-4,
      # ...其他参数
  )

  trainer = Trainer(
      model=model,
      args=training_args,
      train_dataset=your_dataset,
      # ...其他组件
  )

  trainer.train()
  ```

##### **4. 保存 (Saving) - `save_pretrained`**

训练完成后，使用`save_pretrained`方法保存模型。

* **关键特性:** 此方法**仅保存**训练产生的适配器权重（如`adapter_model.bin`）和配置文件（`adapter_config.json`），而**不保存**庞大的基础模型。这使得模型检查点非常小（通常为几MB到几十MB），易于存储和分发。

* **代码示例:**

  ```python
  output_dir = "path/to/adapter"
  model.save_pretrained(output_dir)
  ```

#### **三、 PEFT 模型推理流程**

##### **1. 模型加载 (Loading) - `AutoPeftModel`**

PEFT库提供了`AutoPeftModel`系列类，用于一键式加载PEFT微调过的模型进行推理。

* **核心功能:** `AutoPeftModel.from_pretrained(adapter_path)` 会自动执行以下操作：

  1. 读取适配器目录下的`adapter_config.json`文件。
  2. 从配置文件中识别出所使用的基础模型名称。
  3. 自动从Hugging Face Hub或本地缓存加载相应的基础模型。
  4. 将适配器权重加载并合并到基础模型中。
  5. 返回一个可以直接用于推理的、已经融合了LoRA权重的完整模型。

* **代码示例:**

  ```python
  from peft import AutoPeftModelForCausalLM
  from transformers import AutoTokenizer

  adapter_path = "path/to/adapter" # 训练后保存的适配器路径

  # 一步加载基础模型和适配器
  model = AutoPeftModelForCausalLM.from_pretrained(adapter_path)

  # 分词器通常需要从原始基础模型加载
  tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-1.8B-Chat")
  ```

##### **2. 推理执行 (Inference)**

加载后的模型与标准`transformers`模型使用方法完全一致。

* **代码示例:**

  ```python
  model.to("cuda")
  model.eval()

  inputs = tokenizer("Your prompt text", return_tensors="pt")
  outputs = model.generate(**inputs.to("cuda"), max_new_tokens=100)

  response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
  print(response)
  ```

---

**笔记总结:** PEFT (以LoRA为例) 通过引入并仅训练少量适配器参数，实现了在保持原模型性能的同时，大幅降低了微调的资源消耗。其训练与推理流程与`transformers`库高度集成，通过`LoraConfig`, `get_peft_model`, `AutoPeftModel`等核心API，为大规模语言模型的个性化定制提供了高效、便捷的范式。
