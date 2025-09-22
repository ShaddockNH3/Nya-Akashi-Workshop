import re
import os

# --- 全局配置 ---
INPUT_DIR = "../get_knowledge/ship_profiles_production"
OUTPUT_DIR = "ships"

# --- 核心辅助函数 ---

def preprocess_wikitext(wikitext):
    """
    第一步预处理：在所有解析开始前，净化文本中的特定模板。
    """
    # 循环“解包”，确保多层嵌套的模板能被彻底解开
    for _ in range(5): 
        wikitext = re.sub(r'\{\{悬浮框\|(.*?)\|[\s\S]*?\}\}', r'\1', wikitext, flags=re.DOTALL)
        wikitext = re.sub(r'\{\{黑幕\|(.*?)\}\}', r'\1', wikitext, flags=re.DOTALL)
    
    # "移除" 纯粹的附加信息模板
    wikitext = re.sub(r'\s*\{\{Player[\s\S]*?\}\}', '', wikitext, flags=re.DOTALL)
    
    return wikitext

def clean_final_value(text):
    """
    最终值清理函数：在输出前，将提取出的原始值清理干净。
    """
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\{\{#invoke:彩蛋台词\|解析\|.*?\}\}(.*)', r'\1', text, flags=re.DOTALL).strip()
    text = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\{\{(?:模板:)?(?:画师数据|强化值|小图标|技能图标|ruby)[\s\S]*?\}\}', '', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</?[^>]+>', '', text, flags=re.DOTALL)
    text = re.sub(r'<\/?nowiki>', '', text, flags=re.DOTALL)
    text = re.sub(r'\{\{\s*\}\}', '', text)
    return text.strip()

# --- 核心解析函数 (在“净化后”的文本上工作) ---

def parse_main_template(wikitext):
    """解析舰娘图鉴主模板。"""
    match = re.search(r'\{\{舰娘图[鉴鑑]([\s\S]*?)\n\}\}', wikitext, re.IGNORECASE)
    if not match: return {}
    content = match.group(1).strip()
    data = {}
    parts = re.split(r'\n\s*\|', content)
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            data[key.strip()] = value.strip()
    return data

def parse_skin_templates(wikitext):
    """
    [全新重构] 解析皮肤台词面板，采用“分割区块”策略。
    """
    # 步骤1：以“| 标题N =”作为分隔符，将包含皮肤的文本切分成块
    skin_chunks = re.split(r'\n\s*\|\s*标题\d+\s*=', wikitext)
    
    # 如果切分后不足2块，说明没有找到皮肤
    if len(skin_chunks) < 2:
        return []

    skins = []
    # 步骤2：从第二块开始遍历（第一块是标题前的内容）
    for chunk in skin_chunks[1:]:
        try:
            # 每一块的开头就是标题，直到第一个换行符
            title, content_part = chunk.split('\n', 1)
            title = title.strip()

            # 在这块内容中，精确查找唯一的“台词表格”
            table_match = re.search(r'(\{\{#invoke: 舰娘台词 \| 台词表格[\s\S]*?\}\})', content_part)
            if not table_match:
                continue
            
            skin_content_str = table_match.group(1)
            
            # 步骤3：对这个独立的“台词表格”进行内部解析
            content_inside = skin_content_str.split('|', 2)[-1]
            pairs = re.findall(r'([^=]+?)\s*=\s*(.*?)(?=\s*\|\s*[a-zA-Z_0-9]+\s*=|\s*\}\})', content_inside, re.DOTALL)
            skin_lines = {key.strip(): value.strip() for key, value in pairs if not key.strip().endswith('_mediaFile')}
            skins.append({'title': title, 'lines': skin_lines})
        except (ValueError, IndexError):
            # 如果某个块的格式不规范，安全跳过
            continue
            
    return skins

def parse_character_setting(wikitext):
    """解析角色设定章节。"""
    match = re.search(r'===角色设定===\s*([\s\S]*?)(?:===相关解释===|===相关图片===|\Z)', wikitext)
    if not match: return ""
    
    setting_text = match.group(1).strip()
    setting_text = re.sub(r'</?gallery.*?>', '', setting_text, flags=re.DOTALL)
    setting_text = re.sub(r'翻译：\w+', '', setting_text)
    setting_text = setting_text.replace('<br>', '\n')
    lines = [line.strip() for line in setting_text.split('\n') if line.strip() and not line.strip().startswith('[[File:')]
    return '\n* '.join(lines)

def format_to_markdown(ship_data, skins, setting_text):
    """将解析出的数据格式化为最终的Markdown文本。"""
    # 此函数逻辑保持不变，因为问题出在输入给它的skins数据不完整
    output = []
    
    output.append(f"### 姓名：{clean_final_value(ship_data.get('名称', ''))}")
    if harmony_name := clean_final_value(ship_data.get('和谐名', '')): output.append(f"* **和谐名：** {harmony_name}")
    output.append(f"* **编号：** {clean_final_value(ship_data.get('编号', ''))}")
    output.append(f"* **类型：** {clean_final_value(ship_data.get('类型', ''))}")
    output.append(f"* **稀有度：** {clean_final_value(ship_data.get('稀有度', ''))}")
    output.append(f"* **阵营：** {clean_final_value(ship_data.get('阵营', ''))}")
    output.append("\n")
    output.append("### 角色人设")
    output.append(f"* **身份：** {clean_final_value(ship_data.get('身份', ''))}")
    output.append(f"* **性格：** {clean_final_value(ship_data.get('性格', ''))}")
    output.append(f"* **关键词：** {clean_final_value(ship_data.get('关键词', ''))}")
    output.append(f"* **持有物：** {clean_final_value(ship_data.get('持有物', ''))}")
    output.append(f"* **发色：** {clean_final_value(ship_data.get('发色', ''))}")
    output.append(f"* **瞳色：** {clean_final_value(ship_data.get('瞳色', ''))}")
    output.append(f"* **萌点：** {clean_final_value(ship_data.get('萌点', ''))}")
    output.append("\n")
    if setting_text:
        output.append("### 角色设定")
        output.append(f"* {setting_text}")
        output.append("\n")
    output.append("### 实装与活动")
    output.append(f"* **实装日期：** {clean_final_value(ship_data.get('实装日期', ''))}")
    if related_activity := clean_final_value(ship_data.get('相关活动', '')): output.append(f"* **相关活动：** {related_activity}")
    output.append("\n")

    output.append("### 舰船台词")
    base_lines_map = {
        "登录界面": ["碧蓝航线！"], "舰船型号": ["舰船型号台词"], "自我介绍": ["自我介绍台词"], "获取台词": ["获取台词"], 
        "登录台词": ["登录台词", "登录台词_2"], "查看详情": ["查看详情台词"],
        "主界面": [f'主界面{i}台词' for i in range(1, 10)],
        "触摸台词": ["普通触摸台词", "普通触摸台词_2"], "特殊触摸": ["特殊触摸台词", "特殊触摸台词_2"], 
        "摸头台词": ["摸头台词", "摸头台词_2"],
        "任务提醒": ["任务提醒台词", "任务提醒台词_2"], "任务完成": ["任务完成台词", "任务完成台词_2"], 
        "邮件提醒": ["邮件提醒台词", "邮件提醒台词_2"], "回港台词": ["回港台词", "回港台词_2"],
        "好感度-失望": ["好感度-失望台词"], "好感度-陌生": ["好感度-陌生台词"], "好感度-友好": ["好感度-友好台词"], "好感度-喜欢": ["好感度-喜欢台词"], 
        "好感度-爱": ["好感度-爱台词", "好感度-爱台词_2"], "誓约台词": ["誓约台词"],
        "委托完成": ["委托完成台词", "委托完成台词_2"], "强化成功": ["强化成功台词"], 
        "旗舰开战": ["旗舰开战台词", "旗舰开战台词_2"], "胜利台词": ["胜利台词", "胜利台词_2"], 
        "失败台词": ["失败台词", "失败台词_2"], "技能台词": ["技能台词"], 
        "血量告急": ["血量告急台词", "血量告急台词_2"],
        "彩蛋台词": sorted([k for k in ship_data if k.startswith('彩蛋') and k.endswith('台词')]),
    }
    for key, value_keys in base_lines_map.items():
        valid_lines = [clean_final_value(ship_data.get(v_key)) for v_key in value_keys if ship_data.get(v_key, '').strip()]
        if valid_lines:
            if len(valid_lines) > 1:
                output.append(f"* **{key}：**")
                for line in valid_lines:
                    output.append(f"  * {line}")
            else:
                output.append(f"* **{key}：** {valid_lines[0]}")
    output.append("\n")

    skin_key_map = {
        "desc": "皮肤描述", "unlock": "解锁", "login": "登录台词", "detail": "查看详情", "touch": "触摸台词", 
        "touch2": "特殊触摸", "headtouch": "摸头台词", "mission": "任务提醒", 
        "mission_complete": "任务完成", "mail": "邮件提醒", "home": "回港台词", 
        "feeling5": "好感度-爱", "expedition": "委托完成", "win_mvp": "胜利台词",
        "lose": "失败台词", "hp_warning": "血量告急", "battle": "旗舰开战", "skill": "技能台词",
        "upgrade": "强化成功"
    }
    
    for i, skin in enumerate(skins):
        title = clean_final_value(skin.get('title', f'皮肤{i+1}'))
        lines = skin.get('lines', {})
        output.append(f"### 皮肤{i+1}：{title}")
        main_lines_list = []
        other_lines_dict = {}

        for key, value in lines.items():
            if key.startswith('main_'): main_lines_list.append(value)
            elif key != 'shipName': other_lines_dict[key] = value
        
        sorted_keys = ['desc', 'unlock', 'login', 'detail', 'touch', 'touch2', 'headtouch', 'mission', 'mission_complete', 'mail', 'home', 'expedition', 'feeling5', 'upgrade', 'battle', 'win_mvp', 'lose', 'skill', 'hp_warning']
        for key in other_lines_dict:
            if key not in sorted_keys: sorted_keys.append(key)

        for key in sorted_keys:
            if key in other_lines_dict:
                display_name = skin_key_map.get(key, key.capitalize())
                cleaned_line = clean_final_value(other_lines_dict[key])
                if cleaned_line:
                    output.append(f"* **{display_name}：** {cleaned_line}")
        
        if main_lines_list:
            output.append(f"* **主界面：**")
            for line in sorted(main_lines_list):
                cleaned_line = clean_final_value(line)
                if cleaned_line:
                    output.append(f"  * {cleaned_line}")
        output.append("\n")
        
    return '\n'.join(output).strip() + '\n'

# --- 主程序执行入口 ---
if __name__ == "__main__":
    if not os.path.exists(INPUT_DIR):
        print(f"错误：输入文件夹 '{INPUT_DIR}' 不存在。")
        exit()
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"信息：已创建输出文件夹 '{OUTPUT_DIR}'")

    print("处理开始：预处理->解析->格式化")
    print("="*60)
    
    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.endswith('.md')]
        if not files_to_process:
            print(f"警告：在 '{INPUT_DIR}' 中未找到任何 .md 文件。")
            exit()
    except OSError as e:
        print(f"错误：无法读取输入文件夹 '{INPUT_DIR}': {e}")
        exit()

    total_files = len(files_to_process)
    processed_count, skipped_count, error_count = 0, 0, 0
    
    for index, filename in enumerate(files_to_process):
        input_filepath = os.path.join(INPUT_DIR, filename)
        output_filepath = os.path.join(OUTPUT_DIR, filename)
        
        print(f"处理中 ({index + 1}/{total_files}): {filename} ...")
        
        try:
            with open(input_filepath, 'r', encoding='utf-8') as f:
                wikitext = f.read()

            preprocessed_text = preprocess_wikitext(wikitext)
            ship_data = parse_main_template(preprocessed_text)
            if not ship_data:
                print(f"  -> 警告: 在 {filename} 中未找到有效的舰娘图鉴模板，已跳过。")
                skipped_count += 1
                continue
            
            skins = parse_skin_templates(preprocessed_text)
            setting_text = parse_character_setting(preprocessed_text)
            formatted_md = format_to_markdown(ship_data, skins, setting_text)
            
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_md)
            processed_count += 1
            
        except Exception as e:
            print(f"  -> 错误: 处理 {filename} 时发生异常: {e}")
            error_count += 1
            
    print("="*60)
    print("处理完毕。")
    print(f"总文件数: {total_files} | 成功: {processed_count} | 跳过: {skipped_count} | 失败: {error_count}")
