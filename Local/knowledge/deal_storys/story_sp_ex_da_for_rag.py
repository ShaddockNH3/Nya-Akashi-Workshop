import re
import os

# --- 配置区 ---
# 请在这里设置您的输入和输出文件夹路径

# INPUT_DIR = "../../get_knowledge/activity_stories_production/EX"
# INPUT_DIR = "../../get_knowledge/activity_stories_production/SP"
INPUT_DIR = "../../get_knowledge/activity_stories_production/Daily"

# “成品仓库”：存放处理后 .md 文件的文件夹
# OUTPUT_DIR = "EX"
# OUTPUT_DIR = "SP"
OUTPUT_DIR = "Daily"


# --- 正则表达式“模具”区 ---

# 这个表达式会捕获<span>标签和冒号之间的所有内容，后续再进行清理
RE_DIALOGUE = re.compile(r'^\s*<span .*?>(.*?)：</span><br>')

RE_MAIN_TITLE = re.compile(r"^\s*== (.*?) ==\s*$")
RE_SECTION_TITLE = re.compile(r"\{\{折叠面板\|标题=(.*?)\|.*?\}\}")
RE_CHOICE = re.compile(r"^\s*'''''<span style=\"color:black;\">(选择项\d+：.*?)</span>'''''<br>")
RE_CHOICE_RESPONSE = re.compile(r"'''''<span style=\"color:black;\">（(选择项\d+)）</span>'''''(.*?)<br>")
RE_CLEANUP_TAGS = re.compile(r"\{\{折叠面板\|.*?\}\}|<br>|'''''|^\s*$")
RE_NARRATIVE = re.compile(r"^(?!<span|<|'').*?[^\s>]$")


def clean_speaker_name(raw_text):
    """
    一个专门用来“净化”说话人名字的辅助函数。
    无论原始名字是什么格式，都把它变成干净的文本。
    """
    # 替换 {playername}
    text = raw_text.replace('{playername}', '指挥官')
    
    # 提取 {{AF|名字}} 中的名字
    af_match = re.search(r'\{\{AF\|(.*?)\}\}', text)
    if af_match:
        return af_match.group(1).strip()
        
    # 去除所有HTML标签，比如指挥官的<span...>
    text = re.sub(r'<.*?>', '', text)
    
    # 返回最终清理后的名字
    return text.strip()


def process_story_files(input_dir, output_dir):
    """
    遍历输入目录中的.md文件，将其格式化，并保存到输出目录。
    """
    print("启动自动化剧情格式化程序 (安全输出模式)。")

    # 检查并创建输出文件夹
    if not os.path.exists(output_dir):
        print(f"输出文件夹 '{output_dir}' 不存在，正在为您创建...")
        os.makedirs(output_dir)

    # 检查输入文件夹
    if not os.path.exists(input_dir):
        print(f"错误：输入文件夹 '{input_dir}' 不存在。程序已停止。")
        return

    print(f"\n--- 开始从 '{input_dir}' 读取文件，处理后将存入 '{output_dir}' ---")

    total_processed_count = 0
    for filename in os.listdir(input_dir):
        if not filename.endswith(".md"):
            continue

        input_filepath = os.path.join(input_dir, filename)
        output_filepath = os.path.join(output_dir, filename) # 输出文件与输入文件同名

        print(f"  - 正在格式化: {filename}")

        try:
            with open(input_filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # (这里的核心处理逻辑与上一版完全相同)
            output_lines = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # 1. 主标题
                match = RE_MAIN_TITLE.match(line)
                if match:
                    output_lines.append(f"# {match.group(1).strip()}\n\n")
                    i += 1
                    continue

                # 2. 章节标题
                match = RE_SECTION_TITLE.match(line)
                if match:
                    output_lines.append(f"## {match.group(1).strip()}\n\n")
                    i += 1
                    continue
                
                # 3. 选项块
                if RE_CHOICE.match(line):
                    choices, responses_raw = [], []
                    start_index = i
                    while i < len(lines) and RE_CHOICE.match(lines[i].strip()):
                        choices.append(RE_CHOICE.match(lines[i].strip()).group(1))
                        i += 1
                    
                    while i < len(lines):
                        speaker_line = lines[i].strip()
                        response_line = lines[i+1].strip() if (i+1 < len(lines)) else ""
                        is_speaker = RE_DIALOGUE.match(speaker_line)
                        is_response = RE_CHOICE_RESPONSE.search(response_line)
                        
                        if is_speaker and is_response:
                            responses_raw.append((speaker_line, response_line))
                            i += 2
                        elif speaker_line.startswith("'''''<span") and RE_CHOICE_RESPONSE.search(speaker_line):
                             responses_raw.append(("", speaker_line))
                             i += 1
                        else:
                            break
                    
                    if choices:
                        output_lines.append("---\n#### **【剧情选项】**\n")
                        for choice in choices:
                            parts = choice.split('：', 1)
                            output_lines.append(f"*   **{parts[0]}：** {parts[1]}\n")
                        output_lines.append("\n---\n#### **【选择分支与后续】**\n")
                        for speaker_line, response_line in responses_raw:
                            speaker = "指挥官"
                            if speaker_line:
                                speaker_match = RE_DIALOGUE.match(speaker_line)
                                if speaker_match:
                                    raw_speaker = speaker_match.group(1)
                                    speaker = clean_speaker_name(raw_speaker).replace('指揮官', '指挥官')
                            
                            response_match = RE_CHOICE_RESPONSE.search(response_line)
                            if response_match:
                                tag, text = response_match.groups()
                                full_choice = next((c for c in choices if c.startswith(tag)), "")
                                output_lines.append(f"> **当选择【{full_choice}】时，{speaker}的反应：**\n")
                                output_lines.append(f"> **{speaker}：** {text.strip()}\n\n")
                        output_lines.append("---\n\n")
                    else:
                        i = start_index
                        output_lines.append(lines[i])
                        i += 1
                    continue

                # 4. 普通对话
                match = RE_DIALOGUE.match(line)
                if match:
                    raw_speaker = match.group(1)
                    speaker = clean_speaker_name(raw_speaker).replace('指揮官', '指挥官')
                    dialogue_text = lines[i+1].strip() if i+1 < len(lines) else ""
                    dialogue_text = RE_CLEANUP_TAGS.sub('', dialogue_text).strip()
                    output_lines.append(f"> **{speaker}：**\n> {dialogue_text}\n\n")
                    i += 2
                    continue

                # 5. 叙事文本
                narrative_text = RE_CLEANUP_TAGS.sub('', line).strip()
                if narrative_text and RE_NARRATIVE.match(line):
                    narrative_text = narrative_text.replace('[', '').replace(']', '') # 清理特殊格式
                    output_lines.append(f"{narrative_text}\n\n")
                
                i += 1

            # 将处理好的内容写入到输出文件夹的新文件中
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.writelines(line if line.endswith('\n') else line + '\n' for line in output_lines)
            
            total_processed_count += 1

        except Exception as e:
            print(f"  -> 处理文件 {filename} 时发生错误: {e}")
    
    print(f"\n所有任务已完成。总计处理了 {total_processed_count} 份档案，已全部存入 '{output_dir}' 文件夹。")


# --- 主程序入口 ---
if __name__ == "__main__":
    process_story_files(INPUT_DIR, OUTPUT_DIR)

