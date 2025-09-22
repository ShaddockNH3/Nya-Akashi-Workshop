import requests
import re
import os
import time

# --- 全局配置 ---
API_URL = "https://wiki.biligame.com/blhx/api.php"
COMMAND_PAGE = "碧蓝回忆录文字版" 
# --- 核心修改点：为Daily剧情设定专属的输出目录 ---
OUTPUT_DIR = "activity_stories_production"  # 生产版总输出目录
OUTPUT_SUBDIR_DAILY = os.path.join(OUTPUT_DIR, "Daily") # Daily剧情的专属子目录

HEADERS = {'User-Agent': 'AkashiWorkshop/1.0 (https://github.com/ShaddockNH3/Nya-Akashi-Workshop; shaddock1122@163.com)'}

# --- 核心功能函数 ---

def get_daily_story_list():
    """从指令页面专门识别并提取所有“日常”分类的剧情标题。"""
    print(f"程序启动：正在从 '{COMMAND_PAGE}' 页面专门搜寻“日常”剧情...")
    
    params = {
        "action": "query", 
        "prop": "revisions", 
        "rvprop": "content", 
        "titles": COMMAND_PAGE, 
        "format": "json", 
        "formatversion": "2"
    }
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        wikitext = response.json()["query"]["pages"][0]["revisions"][0]["content"]
    except Exception as e:
        print(f"错误：读取指令页面失败，原因: {e}")
        return []

    # --- 核心修改点：使用我们已验证成功的模式，只匹配“日常” ---
    daily_matches = re.findall(r'\{\{碧蓝回忆录\|([^|]+)\|活动\|日常\}\}', wikitext)
    
    story_list = []
    seen_titles = set()
    for title in daily_matches:
        title = title.strip()
        if title not in seen_titles:
            # 这里的category是固定的，就是"Daily"
            story_list.append({"title": title, "category": "Daily"})
            seen_titles.add(title)

    print(f"识别完成：共找到 {len(story_list)} 个“日常”剧情条目。")
    return story_list

def get_story_wikitext(page_title):
    """获取指定剧情页面的原始Wikitext。(此函数无需改动)"""
    params = {
        "action": "query", 
        "prop": "revisions", 
        "rvprop": "content", 
        "titles": page_title, 
        "redirects": 1, 
        "format": "json", 
        "formatversion": "2"
    }
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if 'error' in data or not data.get("query", {}).get("pages", [{}])[0].get("revisions"):
             return None
        return data["query"]["pages"][0]["revisions"][0]["content"]
    except Exception:
        return None

# --- 主程序执行入口 ---
if __name__ == "__main__":
    # 检查并创建Daily专属的输出目录
    if not os.path.exists(OUTPUT_SUBDIR_DAILY):
        os.makedirs(OUTPUT_SUBDIR_DAILY)
    print(f"已确保输出目录存在: '{OUTPUT_SUBDIR_DAILY}'")

    daily_list = get_daily_story_list()
    
    if daily_list:
        total = len(daily_list)
        print(f"\n准备开始抓取全部 {total} 份“日常”剧情原文...")
        print("="*60)
        
        # 为Daily剧情创建一个独立的编号计数器
        daily_counter = 1
        
        for index, story_info in enumerate(daily_list):
            title = story_info["title"]
            category = story_info["category"] # 这里的值永远是 "Daily"
            print(f"正在处理 ({index + 1}/{total}): {title} ...")
            
            # Daily剧情也是主页面的子页面
            full_page_title = f"{COMMAND_PAGE}/{title}"
            wikitext = get_story_wikitext(full_page_title)

            if wikitext:
                # 目标目录固定为Daily的子目录
                target_dir = OUTPUT_SUBDIR_DAILY
                sequence_num = daily_counter
                daily_counter += 1
                
                # 格式化文件名，序号补零
                filename_prefix = f"{sequence_num:03d}"
                filename_title = re.sub(r'[\\/*?:"<>|]', '_', title)
                
                # 保存为 .md 文件
                filename = f"{filename_prefix}_{filename_title}.md"
                filepath = os.path.join(target_dir, filename)
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(wikitext)
                    print(f"  -> 成功: 已保存至 '{category}' 目录: {filename}")
                except Exception as e:
                    print(f"  -> 错误: 写入文件失败，原因: {e}")
            else:
                print(f"  -> 错误: 未能获取页面 '{full_page_title}' 的原文。")
            
            # 保持礼貌，每次请求后停顿1秒
            time.sleep(1)

        print("="*60)
        print("所有“日常”剧情已处理完毕。")

