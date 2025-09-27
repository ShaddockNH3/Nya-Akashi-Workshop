import os
from huggingface_hub import snapshot_download

# --- 独立配置区 ---
# 请在使用前确认此处的项目根目录是否正确
PROJECT_BASE_PATH = "/root/autodl-tmp/Akashi"

# 根据根目录自动构建嵌入模型的存放路径
EMBEDDING_MODEL_PATH = os.path.join(PROJECT_BASE_PATH, "models/embedding-model")
# --------------------

def download_embedding_model():
    """
    下载项目所需的 sentence-transformers 嵌入模型。
    本脚本为独立版本，不依赖外部配置文件。
    """
    # 确定需要下载的模型名称
    model_id = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    # 从本文件顶部的配置区获取模型应该存放的目标路径
    target_path = EMBEDDING_MODEL_PATH
    
    print("--- 准备下载项目所需的嵌入模型 (独立脚本) ---")
    print(f"  - 模型名称: {model_id}")
    print(f"  - 本地路径: {target_path}")
    print(f"  - (请确保项目根目录配置正确: {PROJECT_BASE_PATH})")


    # 1. 检查目标路径是否已存在模型文件
    #    如果已存在，则跳过下载，避免重复工作。
    if os.path.exists(target_path):
        print("\n✅ 检测到模型已存在于目标路径，无需重复下载。")
        return

    # 2. 如果模型不存在，则开始执行下载流程
    print("\n⏳ 模型不存在，开始从 Hugging Face Hub 下载...")
    
    # 设置 Hugging Face 的国内镜像端点，以提高下载速度
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

    try:
        # 使用 snapshot_download 函数进行下载
        # 它支持断点续传，非常可靠。
        snapshot_download(
            repo_id=model_id,
            local_dir=target_path,
            local_dir_use_symlinks=False, # 推荐使用 False 以获得更好的跨平台兼容性
            resume_download=True,         # 开启断点续传功能
        )
        print("\n✅ 下载成功！嵌入模型已准备就绪。")
        print(f"   模型文件已完整保存至: {target_path}")

    except Exception as e:
        print(f"\n❌ 下载过程中发生错误：{e}")
        print("   请检查您的网络连接是否正常。")
        print("   如果在本地计算机上运行，可能需要配置网络代理。")


if __name__ == "__main__":
    # 当该脚本被直接执行时，调用下载函数
    download_embedding_model()
