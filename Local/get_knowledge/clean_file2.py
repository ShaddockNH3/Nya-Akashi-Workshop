import os

# --- 【核心配置】---
# 同样，请将这个路径设置为您存放那些已经重命名好的 .md 文件的文件夹
TARGET_DIR = r"activity_stories_production/File"

def sync_markdown_titles_from_filenames(directory):
    """
    遍历指定目录，将每个 .md 文件内的H1标题(#)更新为与文件名一致。
    文件名格式应为: '序号_标题.md'
    """
    print(f"[任务开始] 正在同步文件夹内的Markdown标题: '{directory}'")
    print("=" * 70)

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

    print(f"发现 {total_files} 个 .md 文件，准备开始同步标题...")

    updated_count = 0
    skipped_count = 0
    for filename in md_files:
        filepath = os.path.join(directory, filename)

        try:
            # --- 步骤一：从文件名提取新标题 ---
            # 首先移除.md后缀
            base_name = os.path.splitext(filename)[0]
            # 按第一个下划线分割
            parts = base_name.split('_', 1)

            # 检查文件名格式是否正确 (必须包含 '序号_标题')
            if len(parts) < 2:
                print(f"  -> [跳过] 文件 '{filename}' 不符合 '序号_标题.md' 格式。")
                skipped_count += 1
                continue
            
            new_title_text_from_filename = parts[1]

            # --- 步骤二：读取文件内容 ---
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines() # 读取所有行到列表中

            if not lines:
                print(f"  -> [跳过] 文件 '{filename}' 是空的。")
                skipped_count += 1
                continue

            # --- 步骤三：替换第一行H1标题 ---
            # 检查第一行是否是H1标题
            if lines[0].strip().startswith('#'):
                original_title = lines[0].strip()
                new_title_line = f"# {new_title_text_from_filename}\n"

                # 如果新旧标题不同，才进行修改和写入
                if lines[0] != new_title_line:
                    lines[0] = new_title_line
                    
                    # --- 步骤四：写回修改后的内容 ---
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    
                    print(f"  -> [成功] 更新了 '{filename}' 的标题为: '{new_title_text_from_filename}'")
                    updated_count += 1
                else:
                    print(f"  -> [跳过] '{filename}' 的标题已是最新，无需更改。")
                    skipped_count += 1
            else:
                print(f"  -> [跳过] '{filename}' 的第一行不是H1标题，未作修改。")
                skipped_count += 1

        except Exception as e:
            print(f"  -> [错误] 处理文件 '{filename}' 时发生意外: {e}")
            skipped_count += 1
            
    print("=" * 70)
    print(f"[任务完成] 共更新了 {updated_count} 个文件，跳过了 {skipped_count} 个文件。")


# --- 主程序执行入口 ---
if __name__ == "__main__":
    sync_markdown_titles_from_filenames(TARGET_DIR)

