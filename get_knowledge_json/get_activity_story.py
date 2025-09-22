import requests
import re
import json
import os
import time

# --- 全局配置 ---
API_URL = "https://wiki.biligame.com/blhx/api.php"
COMMAND_PAGE = "碧蓝回忆录文字版" 
OUTPUT_DIR = "activity_stories_production"  # 生产版输出目录
OUTPUT_SUBDIR_EX = os.path.join(OUTPUT_DIR, "EX")
OUTPUT_SUBDIR_SP = os.path.join(OUTPUT_DIR, "SP")

HEADERS = {'User-Agent': 'AkashiWorkshop (https://github.com/ShaddockNH3/Nya-Akashi-Workshop; shaddock1122@163.com)'}

# --- 核心功能函数 ---

def get_activity_story_list():
    """从指令页面识别并提取所有活动剧情的标题和分类(EX/SP)。"""
    print(f"程序启动：正在从 '{COMMAND_PAGE}' 页面识别活动剧情...")
    
    params = {"action": "query", "prop": "revisions", "rvprop": "content", 
              "titles": COMMAND_PAGE, "format": "json", "formatversion": "2"}
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        wikitext = response.json()["query"]["pages"][0]["revisions"][0]["content"]
    except Exception as e:
        print(f"错误：读取指令页面失败，原因: {e}")
        return []

    # 使用正则表达式精确匹配活动剧情的标题和分类
    activity_matches = re.findall(r'\{\{碧蓝回忆录\|([^|]+)\|活动\|(EX|SP)\}\}', wikitext)
    
    story_list = []
    seen_titles = set()
    for title, category in activity_matches:
        title = title.strip()
        if title not in seen_titles:
            story_list.append({"title": title, "category": category})
            seen_titles.add(title)

    print(f"识别完成：共找到 {len(story_list)} 个活动剧情条目。")
    return story_list

def get_story_wikitext(page_title):
    """获取指定剧情页面的原始Wikitext。"""
    params = {"action": "query", "prop": "revisions", "rvprop": "content", "titles": page_title, 
              "redirects": 1, "format": "json", "formatversion": "2", "maxlag": "5"}
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        # 检查API错误或页面无内容
        if 'error' in data or not data.get("query", {}).get("pages", [{}])[0].get("revisions"):
             return None
        return data["query"]["pages"][0]["revisions"][0]["content"]
    except Exception:
        return None

# --- 主程序执行入口 ---
if __name__ == "__main__":
    # 检查并创建输出目录结构
    if not os.path.exists(OUTPUT_SUBDIR_EX):
        os.makedirs(OUTPUT_SUBDIR_EX)
    if not os.path.exists(OUTPUT_SUBDIR_SP):
        os.makedirs(OUTPUT_SUBDIR_SP)
    print(f"已确保输出目录存在: '{OUTPUT_DIR}'")

    activity_list = get_activity_story_list()
    
    if activity_list:
        total = len(activity_list)
        print(f"\n准备开始抓取全部 {total} 份活动剧情原文...")
        print("="*60)
        
        # EX和SP剧情的独立编号计数器
        ex_counter = 1
        sp_counter = 1
        
        # 遍历所有已识别的活动剧情
        for index, story_info in enumerate(activity_list):
            title = story_info["title"]
            category = story_info["category"]
            print(f"正在处理 ({index + 1}/{total}): {title} (分类: {category}) ...")
            
            # 拼接构成实际的子页面URL标题
            full_page_title = f"{COMMAND_PAGE}/{title}"
            wikitext = get_story_wikitext(full_page_title)

            if wikitext:
                story_data = {
                    "title": title,
                    "category": category,
                    "raw_wikitext": wikitext
                }
                
                # 根据分类决定输出目录和文件序号
                if category == 'EX':
                    target_dir = OUTPUT_SUBDIR_EX
                    sequence_num = ex_counter
                    ex_counter += 1
                else:  # category == 'SP'
                    target_dir = OUTPUT_SUBDIR_SP
                    sequence_num = sp_counter
                    sp_counter += 1
                
                # 格式化文件名，序号补零以方便排序
                filename_prefix = f"{sequence_num:03d}"
                filename_title = re.sub(r'[\\/*?:"<>|]', '_', title)
                filename = f"{filename_prefix}_{filename_title}.json"
                
                filepath = os.path.join(target_dir, filename)
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(story_data, f, ensure_ascii=False, indent=4)
                    print(f"  -> 成功: 已保存至 '{category}' 目录: {filename}")
                except Exception as e:
                    print(f"  -> 错误: 写入文件失败，原因: {e}")
            else:
                print(f"  -> 错误: 未能获取页面 '{full_page_title}' 的原文。")
            
            # 遵守礼仪，在每次请求后停顿1秒
            time.sleep(1)

        print("="*60)
        print("所有活动剧情已处理完毕。")