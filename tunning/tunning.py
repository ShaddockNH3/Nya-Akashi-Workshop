# ------------ “明石AI”人格注入 - 完整微调代码 ------------
# 这次我们需要安装一些更专业的工具！
# !pip install -U transformers datasets accelerate peft trl bitsandbytes

import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer

# --- 1. 准备阶段：加载我们的“演员”和“剧本” ---

# 【新变化！】选择我们的“演员”：一个强大的中文对话模型
# 这里以 Qwen1.5 的一个较小但依然强大的版本为例，方便运行
model_id = "Qwen/Qwen1.5-1.8B-Chat" 

# 【新变化！】加载我们的“剧本”文件
data_file_path = "akashi_persona_script.jsonl"
dataset = load_dataset("json", data_files=data_file_path, split="train")

# --- 2. 演员的“上妆”与“排练场”的特殊配置 ---

# 【新技巧！】为了在有限的资源（比如Colab的GPU）上训练大模型，我们需要一些“魔法”
# BitsAndBytesConfig (量化): 就像是给演员穿上一件轻便的训练服，而不是沉重的盔甲。
# 它能用更少的显存加载模型，但几乎不损失性能！
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# 加载模型，并同时应用上面的“量化”魔法
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto" # 自动把模型分配到可用的设备上（比如GPU）
)

# 加载演员对应的 Tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)
# 大语言模型的tokenizer需要一个padding_token，如果没有就用eos_token代替
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# 【新技巧！】LoraConfig (参数高效微调PEFT): 这才是真正的“省钱”大魔法！
# 我们不调整演员的每一块肌肉（全部参数），那样太耗费资源了。
# 我们只在他身上加装一些轻便的、可训练的“外骨骼”（LoRA层）。
# 训练时，我们只训练这些“外骨骼”，演员本体的肌肉保持不变。
# 这样做能用极小的资源，达到几乎和完全微调一样的效果！
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # 告诉“外骨骼”要安装在哪些关键关节上
    task_type="CAUSAL_LM",
)


# --- 3. 聘请“金牌导演” SFTTrainer，并设定“排练计划” ---

# TrainingArguments: 这就是我们的“排练计划表”，告诉导演所有细节
training_args = TrainingArguments(
    output_dir="./akashi_ai_results",      # 排练成果的存放目录
    num_train_epochs=3,                  # 总共排练3遍剧本
    per_device_train_batch_size=4,       # 每次拿4句台词进行排练
    gradient_accumulation_steps=2,       # 累积几次梯度再更新，变相增大batch size
    optim="paged_adamw_8bit",            # 一位非常节省内存的“私人教练”
    logging_steps=10,                    # 每排练10次，就记录一下进度
    learning_rate=2e-4,                  # 学习力度（排练强度）
    fp16=True,                           # 使用混合精度训练，更快更省
)

# 实例化我们的“金牌导演”！
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    peft_config=peft_config,             # 把“外骨骼”方案交给导演
    dataset_text_field="text",           # 【新变化！】告诉导演，我们的剧本格式是什么样的
                                         # SFTTrainer默认需要一个text字段，我们需要处理一下数据格式
    # SFTTrainer 需要特定格式，我们定义一个函数来创建这个格式
    formatting_func=lambda example: f"指令: {example['instruction']}\n输入: {example['input']}\n输出: {example['output']}",
    max_seq_length=1024,                 # 每段台词最长不超过1024个字
    args=training_args,                  # 把排练计划表交给导演
)


# --- 4. 开始排练！Action! ---

print("开始注入'明石'灵魂！排练开始...")
trainer.train()


# --- 5. 杀青！保存我们独一无二的“明石AI”！---

print("\n排练完成！正在保存我们专属的'明石AI'...")
output_dir = "akashi-ai-v1"
trainer.save_model(output_dir)

print(f"注入灵魂的'明石AI'已成功保存到 '{output_dir}' 文件夹！准备好和她对话吧！喵！")

