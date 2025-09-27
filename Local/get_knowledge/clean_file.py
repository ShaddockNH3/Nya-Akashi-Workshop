import os
import re

# --- 【核心配置】---
# 请将这个路径设置为您存放那些需要处理的 .md 文件的文件夹
# 例如，如果文件在 'D:\Akashi\archives'，就这样写
# 注意：路径中的反斜杠 \ 最好写成双反斜杠 \\ 或者在前面加 r
TARGET_DIR = r"activity_stories_production/Fil" 

def clean_and_rename_files(directory):
    """
    遍历指定目录下的所有 .md 文件，进行净化和重命名操作。
    """
    print(f"[任务开始] 正在扫描目标文件夹: '{directory}'")
    print("=" * 60)

    # 检查目录是否存在
    if not os.path.isdir(directory):
        print(f"[错误] 找不到目标文件夹: '{directory}'")
        print("请检查 TARGET_DIR 的路径是否正确！")
        return

    # 获取所有 .md 文件列表
    md_files = [f for f in os.listdir(directory) if f.endswith('.md')]
    total_files = len(md_files)

    if total_files == 0:
        print("[完成] 目标文件夹中没有找到任何 .md 文件。")
        return

    print(f"发现 {total_files} 个 .md 文件，准备开始处理...")

    processed_count = 0
    for filename in md_files:
        original_filepath = os.path.join(directory, filename)
        
        try:
            # --- 步骤一：读取并净化内容 ---
            with open(original_filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 删除所有的换行符
            cleaned_content = content.replace('\\n', '')

            # --- 步骤二：寻找新的文件名 ---
            # 使用正则表达式匹配第一组连续的中文字符
            # [\u4e00-\u9fa5] 是中文字符的Unicode范围
            match = re.search(r'[\u4e00-\u9fa5]+', cleaned_content)
            
            if not match:
                print(f"  -> [警告] 在文件 '{filename}' 中未找到中文字符，已跳过重命名。")
                continue

            first_chinese_text = match.group(0)

            # --- 步骤三：构建新的文件名 ---
            # 提取原文件名的序号前缀 (例如 "001_")
            name_parts = filename.split('_', 1)
            if len(name_parts) > 1 and name_parts[0].isdigit():
                prefix = name_parts[0]
                new_filename = f"{prefix}_{first_chinese_text}.md"
            else:
                # 如果原文件名没有序号，则不加前缀
                print(f"  -> [提示] 文件 '{filename}' 没有标准序号前缀，将直接使用新名称。")
                new_filename = f"{first_chinese_text}.md"

            new_filepath = os.path.join(directory, new_filename)

            # --- 步骤四：写入净化后的内容并重命名 ---
            # 1. 先将净化后的内容写回原文件
            with open(original_filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            # 2. 然后执行重命名
            #    为了避免重名文件覆盖，先检查新文件名是否存在
            if os.path.exists(new_filepath) and original_filepath != new_filepath:
                 print(f"  -> [警告] 新文件名 '{new_filename}' 已存在，为避免覆盖，已跳过文件 '{filename}' 的重命名。")
            else:
                os.rename(original_filepath, new_filepath)
                print(f"  -> [成功] '{filename}'  ->  '{new_filename}'")
                processed_count += 1

        except Exception as e:
            print(f"  -> [错误] 处理文件 '{filename}' 时发生意外: {e}")

    print("=" * 60)
    print(f"[任务完成] 共处理了 {processed_count} / {total_files} 个文件。")


# --- 主程序执行入口 ---
if __name__ == "__main__":
    clean_and_rename_files(TARGET_DIR)
