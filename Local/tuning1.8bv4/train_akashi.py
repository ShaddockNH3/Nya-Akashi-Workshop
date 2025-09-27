import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer

# 阶段一: 定义模型、数据路径及加载
model_id = "Qwen/Qwen1.5-1.8B-Chat"
data_file_path = "/content/drive/MyDrive/Akashi_Project/akashi_persona_script.jsonl"
full_dataset = load_dataset("json", data_files=data_file_path, split="train")

train_validation_split = full_dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = train_validation_split['train']
eval_dataset = train_validation_split['test']

# 阶段二: 模型与Tokenizer的配置与加载
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = 'right' # 明确指定填充方向，防止潜在警告

# 阶段三: PEFT (LoRA) 与训练参数配置
peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    task_type="CAUSAL_LM",
)
training_args = TrainingArguments(
    output_dir="/content/drive/MyDrive/Akashi_Project/akashi_1.8b_results",
    do_eval=True,
    eval_steps=10,
    num_train_epochs=4,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    optim="paged_adamw_8bit",
    logging_steps=10,
    learning_rate=2e-4,
    fp16=True,
)

# 阶段四: 实例化SFTTrainer并开始训练
def formatting_prompts_func(example):
    text = f"### 指令:\n{example['instruction']}\n\n### 输入:\n{example['input']}\n\n### 输出:\n{example['output']}"
    return text # 直接返回格式化好的字符串

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    peft_config=peft_config,
    formatting_func=formatting_prompts_func,
)

# 启动训练
print("开始训练")
trainer.train()

# 阶段五: 保存微调后的模型
output_dir = "/content/drive/MyDrive/Akashi_Project/akashi-ai-1.8b-v4"
print(f"\n训练完成！正在保存LoRA适配器到: {output_dir}")
trainer.save_model(output_dir)

print(f"模型已成功保存!")
