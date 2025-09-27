# download_model.py

import os
from huggingface_hub import snapshot_download
import logging

# --- 请在这里配置 ---
# 1. 你的 Hugging Face Access Token
# 把下面这串假的 hf_... 换成你自己的真实 Token
token = "hf_xxxx" 

# 2. 你想下载的模型 ID
model_id = "Qwen/Qwen1.5-7B-Chat"

# 3. 你想把模型保存在本地的哪个文件夹
local_dir = "../models/Qwen1.5-7B-Chat"
# --- 配置结束 ---

# 设置日志，方便我们看到更详细的下载信息
logging.basicConfig(level=logging.INFO)

# 确保目标文件夹存在
os.makedirs(local_dir, exist_ok=True)

print(f"准备开始下载模型: {model_id}")
print(f"将保存到本地路径: {os.path.abspath(local_dir)}")
print("="*50)

try:
    # 开始下载！
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        token=token,
        resume_download=True,
        local_dir_use_symlinks=False, # 在AutoDL上建议设为False，更稳定
    )
    print("\n" + "="*50)
    print("🎉 模型下载成功！")

except Exception as e:
    print(f"\n" + "="*50)
    print(f"呜喵... 下载过程中发生错误: {e}")

