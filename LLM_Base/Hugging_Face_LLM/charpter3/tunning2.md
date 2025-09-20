### **技术笔记：使用 Trainer API 进行模型微调**

本章旨在阐述 `transformers` 库中高级 `Trainer` API 的使用方法，该 API 旨在简化标准模型微调流程，将手动编写的训练循环抽象化。

#### 1. `Trainer` 的配置与初始化

在实例化 `Trainer` 之前，必须配置两个核心对象：`TrainingArguments` 和模型本身。

* **`TrainingArguments` (训练参数):**
  此数据类封装了训练与评估过程中所有可配置的超参数。其**唯一必须的参数**是 `output_dir`，用于指定模型检查点（checkpoints）和其他训练产物（如日志）的保存路径。其他参数（如学习率、批处理大小等）均有默认值，适用于基础的微调任务。

  ```python
  from transformers import TrainingArguments

  # 初始化训练参数，指定输出目录
  training_args = TrainingArguments("test-trainer")
  ```

* **模型实例化:**
  与之前章节类似，使用 `AutoModelForSequenceClassification` 加载预训练模型。关键在于需指定 `num_labels` 以匹配特定任务的类别数量。

  ```python
  from transformers import AutoModelForSequenceClassification

  model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)
  ```

  **注意:** 加载模型时，系统会产生一条警告，提示部分权重被随机初始化（`['classifier.bias', 'classifier.weight']`）。这是一个**预期行为**，而非错误。它表明预训练模型的基础部分被成功加载，而特定于下游任务的分类头（classifier head）被丢弃，并替换为一个新的、未经训练的分类头。这正是微调（fine-tuning）的起点。

* **`Trainer` 实例化:**
  `Trainer` 对象是训练过程的执行器。它整合了所有必要的组件。

  ```python
  from transformers import Trainer

  trainer = Trainer(
      model=model,
      args=training_args,
      train_dataset=tokenized_datasets["train"],
      eval_dataset=tokenized_datasets["validation"],
      data_collator=data_collator,
      tokenizer=tokenizer,
  )
  ```

  **说明:** 若在初始化时提供了 `tokenizer`，`Trainer` 能够自动使用一个标准的 `DataCollatorWithPadding` 实例。因此，`data_collator` 参数在此场景下是可选的。

#### 2. 执行训练与评估

定义 `Trainer` 后，通过调用其 `train()` 方法即可启动微调。

```python
trainer.train()
```

在默认配置下，训练过程仅会报告训练损失（Training Loss）。为了在训练中监控模型在验证集上的真实性能，必须配置评估策略。

#### 3. 构建评估函数 `compute_metrics`

为了使 `Trainer` 能够在评估阶段计算除损失（loss）之外的指标（如准确率），需要定义并传递一个 `compute_metrics` 函数。

* **函数签名:** 该函数接收一个 `EvalPrediction` 对象，其包含 `predictions` (模型的原始输出，即 logits) 和 `label_ids` (真实标签) 两个字段。函数必须返回一个字典，其键为指标名称（字符串），值为指标的计算结果（浮点数）。

* **核心步骤:**

  1. **Logits 转换:** 模型的直接输出是 logits，一个二维数组。需要使用 `numpy.argmax(logits, axis=-1)` 沿最后一个维度找到最大值的索引，将其转换为最终的预测类别。
  2. **加载指标:** 使用 `evaluate.load()` 函数从 `evaluate` 库中加载适用于特定任务的评估脚本（例如 `"glue"`, `"mrpc"`）。
  3. **计算指标:** 调用加载的 `metric` 对象的 `compute()` 方法，传入模型的预测结果 (`predictions`) 和真实标签 (`references`)。

* **完整实现:**

  ```python
  import numpy as np
  import evaluate

  def compute_metrics(eval_preds):
      # 加载与任务匹配的评估指标
      metric = evaluate.load("glue", "mrpc")
      logits, labels = eval_preds
      # 将 logits 转换为预测标签
      predictions = np.argmax(logits, axis=-1)
      # 使用真实标签和预测标签计算指标
      return metric.compute(predictions=predictions, references=labels)
  ```

#### 4. 整合评估并重新训练

为了在训练的每个 epoch 结束时都进行评估，需要使用更新后的参数重新初始化 `Trainer`。

* **关键步骤:**

  1. 在 `TrainingArguments` 中设置 `evaluation_strategy="epoch"`。
  2. 在 `Trainer` 初始化时，传入 `compute_metrics` 函数。
  3. **重要:** 重新实例化模型 (`AutoModelForSequenceClassification.from_pretrained(...)`)。若不这样做，`trainer.train()` 将会在已训练过的模型上继续训练，而不是从头开始一个新的微调过程。

* **最终代码:**

  ```python
  # 1. 更新训练参数以启用基于 epoch 的评估
  training_args = TrainingArguments("test-trainer", evaluation_strategy="epoch")
  # 2. 重新加载一个未经微调的“干净”模型
  model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

  trainer = Trainer(
      model=model,
      args=training_args,
      train_dataset=tokenized_datasets["train"],
      eval_dataset=tokenized_datasets["validation"],
      data_collator=data_collator,
      tokenizer=tokenizer,
      # 3. 传入我们定义的评估函数
      compute_metrics=compute_metrics,
  )

  trainer.train()
  ```

通过以上配置，`Trainer` 将在每个 epoch 结束后，自动在验证集上计算并报告损失、准确率、F1 分数等指标，从而实现了对训练过程的全面监控。
