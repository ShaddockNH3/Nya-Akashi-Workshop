import os
import re

# 定义输入和输出目录
INPUT_DIR = os.path.join("../../get_knowledge/activity_stories_production", "Character")
OUTPUT_DIR = "Character"

def parse_story_file_advanced(file_content):
    """
    解析故事文件内容，提取标题、章节、对话、旁白和选项。

    Args:
        file_content (str): 从文件读取的原始字符串内容。

    Returns:
        dict: 一个结构化的字典，包含故事的全部信息。
    """
    story_data = {
        "title": "",
        "sections": []
    }
    
    title_match = re.search(r'^#\s*(.*)', file_content, re.MULTILINE)
    if title_match:
        story_data["title"] = title_match.group(1).strip()
    
    sections_raw = re.split(r'\n##\s+', file_content)
    if sections_raw and title_match and title_match.group(0) in sections_raw[0]:
        sections = sections_raw[1:]
    else:
        sections = sections_raw

    for section_text in sections:
        if not section_text.strip():
            continue

        section_data = {
            "subtitle": "",
            "content": []
        }
        
        subtitle_match = re.search(r'^(.*?)\s*展开/折叠', section_text)
        if subtitle_match:
            section_data["subtitle"] = subtitle_match.group(1).strip()
            
        content_block = re.sub(r'</?p>', '', section_text, flags=re.IGNORECASE)
        lines = [line.strip() for line in content_block.split('<br/>') if line.strip()]
        
        for line in lines:
            if re.match(r'^\s*[一二三四五六七八九十]+\s+', line) or line.strip() == story_data["title"]:
                continue

            # 匹配选项
            choice_match = re.search(r'<i><b><span style="color:black;">(.*?)</span></b></i>', line)
            if choice_match:
                section_data["content"].append({
                    "type": "choice",
                    "text": choice_match.group(1).strip()
                })
                continue
            
            # 匹配对话
            dialogue_match = re.search(r'<span(?: class="AF"| style="color:#4eb24e;")>(.*?)</span>：', line)
            if dialogue_match:
                character_name_raw = dialogue_match.group(1)
                character_name = re.sub(r'</?span.*?>', '', character_name_raw).strip()
                dialogue_text = line[dialogue_match.end():].strip()
                
                if dialogue_text:
                    section_data["content"].append({
                        "type": "dialogue",
                        "character": character_name,
                        "line": dialogue_text
                    })
                continue
                
            # 其余视为旁白
            narrative_text = re.sub(r'</?span.*?>', '', line).strip()
            if narrative_text and "展开/折叠" not in narrative_text and narrative_text != '……':
                section_data["content"].append({
                    "type": "narrative",
                    "text": narrative_text
                })

        if section_data["subtitle"] or section_data["content"]:
            story_data["sections"].append(section_data)
        
    return story_data

def format_as_markdown_advanced(story_data):
    """
    将解析后的故事数据格式化为干净的Markdown文本。

    Args:
        story_data (dict): 由解析函数生成的结构化字典。

    Returns:
        str: 格式化后的Markdown字符串。
    """
    md_lines = []
    
    if story_data['title']:
        md_lines.append(f"# {story_data['title']}")
    
    for section in story_data['sections']:
        md_lines.append("")
        md_lines.append(f"## {section['subtitle']}")
        md_lines.append("")
        
        last_character = None
        
        for item in section['content']:
            item_type = item.get("type")
            
            if item_type == "dialogue":
                character = item["character"]
                line_text = item["line"]
                
                if character != last_character:
                    if last_character is not None:
                        md_lines.append("")
                    md_lines.append(f"**{character}：**")
                    last_character = character
                
                md_lines.append(f"> {line_text}")

            elif item_type == "narrative":
                md_lines.append(item['text'])
                md_lines.append("")
                last_character = None
                
            elif item_type == "choice":
                md_lines.append(f"***{item['text']}***")
                md_lines.append("")
                last_character = None
    
    return "\n".join(md_lines)

def process_all_files():
    """
    处理输入目录中的所有.md文件，并将转换后的文件保存到输出目录。
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.isdir(INPUT_DIR):
        print(f"错误：找不到输入目录 '{INPUT_DIR}'")
        return

    print(f"开始处理目录 '{INPUT_DIR}' 中的文件...")

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            try:
                print(f"正在处理文件: {filename} ...")
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在解析前，将 "undefined" 替换为 "指挥官"
                content = content.replace("undefined", "指挥官")
                
                parsed_data = parse_story_file_advanced(content)
                markdown_output = format_as_markdown_advanced(parsed_data)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_output)
                
                print(f"文件 {filename} 已成功处理。")

            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {e}")

    print(f"\n全部处理完毕。输出文件已保存至 '{OUTPUT_DIR}' 目录。")


if __name__ == "__main__":
    process_all_files()
