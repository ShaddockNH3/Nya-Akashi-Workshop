import os
import re

# --- 配置区 ---
TARGET_DIR = os.path.join("activity_stories_production", "Character")


def rename_md_files_by_title(directory):
    """
    遍历指定目录中的所有.md文件，并根据其内部的第一个H1标题进行重命名。
    """
    print("喵！启动档案命名标准化程序！")
    
    # 检查目标文件夹是否存在
    if not os.path.isdir(directory):
        print(f"呜哇！找不到档案室 '{directory}'！请主人様检查一下文件夹路径哦。")
        return

    print(f"目标档案室: '{directory}'")
    print("="*60)
    
    renamed_count = 0
    skipped_count = 0
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(directory):
        # 确保我们只处理 .md 文件
        if not filename.endswith(".md"):
            continue
            
        old_filepath = os.path.join(directory, filename)
        
        # 步骤1：从旧文件名中提取编号
        # 我们用正则表达式来安全地匹配开头的三个数字
        match = re.match(r'(\d{3})', filename)
        if not match:
            print(f"  -> 警告：文件 '{filename}' 的开头不是标准三位数编号，已跳过。")
            skipped_count += 1
            continue
        
        number_prefix = match.group(1) # 这就是 "001", "002" 等
        
        # 步骤2：打开文件，读取第一个H1标题
        new_title = None
        try:
            with open(old_filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    # 找到第一个以 '# ' 开头的行
                    if line.strip().startswith('# '):
                        # 提取标题文本，去掉'# '和两边的空格
                        new_title = line.strip()[2:].strip()
                        break # 找到后就不用再读了
        except Exception as e:
            print(f"  -> 错误：读取文件 '{filename}' 时发生意外，已跳过。原因: {e}")
            skipped_count += 1
            continue

        if not new_title:
            print(f"  -> 警告：在文件 '{filename}' 中未能找到一级标题(以'# '开头)，已跳过。")
            skipped_count += 1
            continue
            
        # 步骤3：清理标题，使其成为合法的文件名
        # 替换掉所有Windows文件名不允许的特殊字符
        cleaned_title = re.sub(r'[\\/*?:"<>|]', '_', new_title)
        
        # 步骤4：组装新文件名并执行重命名
        new_filename = f"{number_prefix}_{cleaned_title}.md"
        new_filepath = os.path.join(directory, new_filename)
        
        # 如果新旧文件名不一样，才进行重命名
        if new_filename != filename:
            try:
                os.rename(old_filepath, new_filepath)
                print(f"  -> 成功: '{filename}'  =>  '{new_filename}'")
                renamed_count += 1
            except Exception as e:
                print(f"  -> 错误：重命名文件 '{filename}' 失败，已跳过。原因: {e}")
                skipped_count += 1
        else:
            # 如果文件名本来就是正确的，就不需要操作啦
            skipped_count += 1

    print("="*60)
    print(f"整理完毕！共成功重命名 {renamed_count} 份档案，跳过 {skipped_count} 份。")

# --- 主程序执行入口 ---
if __name__ == "__main__":
    rename_md_files_by_title(TARGET_DIR)
