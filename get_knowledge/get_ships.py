import requests
import time
import os
import re

# --- 全局配置 ---
API_URL = "https://wiki.biligame.com/blhx/api.php"
OUTPUT_DIR = "ship_profiles_production"  # 输出文件夹名称

# 规范化请求头，确保我们的访问行为友好且可识别
HEADERS = {
    'User-Agent': 'AkashiWorkshop (https://github.com/ShaddockNH3/Nya-Akashi-Workshop; shaddock1122@163.com)',
    'Accept-Encoding': 'gzip', # 启用Gzip压缩，节约带宽
}

# 最终验证过的 分类 -> 文件名前缀 映射表
CATEGORY_PREFIX_MAP = {
    "Category:舰娘": "REGULAR",
    "Category:META舰娘": "META",
    "Category:联动舰娘": "COLLAB",
    "Category:方案舰娘": "PR",
    "Category:II型舰娘": "II",
}

# --- 核心功能函数 ---

def get_all_ship_data():
    """获取所有舰船页面的名称及其所属的主要分类。"""
    print("启动全舰船扫描程序，准备扫描所有指定分类...")
    
    categories_to_scan = list(CATEGORY_PREFIX_MAP.keys())
    ship_data_map = {}  # 使用字典来存储 舰船名 -> 分类，可以自动去重

    for category in categories_to_scan:
        print(f"\n--- 正在扫描分类: {category} ---")
        # 基础API参数，增加了maxlag以遵守使用礼仪
        params = {
            "action": "query", 
            "list": "categorymembers", 
            "cmtitle": category, 
            "cmlimit": "500", 
            "format": "json", 
            "formatversion": "2",
            "maxlag": "5"  # 遵守礼仪：当服务器繁忙时，最长等待5秒
        }
        continue_params = {}
        count_in_category = 0
        while True:
            current_params = params.copy()
            current_params.update(continue_params)
            try:
                response = requests.get(API_URL, params=current_params, headers=HEADERS)
                response.raise_for_status()  # 如果请求出错 (如 404, 503)，则会抛出异常
                data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"错误: 扫描分类 {category} 时网络请求失败: {e}")
                break
            
            # 检查API是否因为服务器繁忙(maxlag)而返回错误
            if 'error' in data and data['error']['code'] == 'maxlag':
                retry_after = int(data['error'].get('info', '5').split(' ')[-2])
                print(f"服务器繁忙，API要求等待 {retry_after} 秒后重试...")
                time.sleep(retry_after)
                continue # 重新尝试刚才的请求

            pages = data.get("query", {}).get("categorymembers", [])
            if not pages and count_in_category == 0:
                print(f"警告: 分类 {category} 未返回任何成员，请检查分类名称是否正确。")

            for page in pages:
                title = page["title"]
                # 过滤掉页面本身是分类或模板的情况
                if not title.startswith("Category:") and not title.startswith("Template:"):
                    ship_data_map[title] = category
                    count_in_category += 1

            if 'continue' in data:
                continue_params = data['continue']
                time.sleep(1)  # 礼貌性延迟，避免过于频繁地请求
            else:
                print(f"此分类扫描完毕。共发现 {count_in_category} 个有效页面。")
                break
    
    all_ships_with_category = sorted(ship_data_map.items())
    print(f"\n全部分类扫描完成。共找到 {len(all_ships_with_category)} 个不重复的舰船档案。")
    return all_ships_with_category

def get_ship_wikitext(ship_name):
    """获取指定舰船页面的原始wikitext文本。"""
    params = {"action": "query", "prop": "revisions", "rvprop": "content", "titles": ship_name,
              "format": "json", "formatversion": "2", "maxlag": "5"}
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if 'error' in data: # 同样检查maxlag
             return None
        # 增加一个检查，确保页面和内容真的存在
        page = data.get("query", {}).get("pages", [{}])[0]
        if "revisions" in page and page["revisions"]:
            return page["revisions"][0]["content"]
        else:
            print(f"  -> 警告: 页面 '{ship_name}' 存在但没有找到内容。")
            return None
    except Exception as e:
        print(f"  -> 错误: 获取 {ship_name} 的wikitext时发生异常: {e}")
        return None
    
def parse_ship_info_to_dict(wikitext, original_title):
    """从wikitext中解析出关键信息，并存入一个字典。"""
    ship_data = {"id": "NO.Unknown", "name": original_title, "raw_wikitext": wikitext}
    # 解析编号
    id_match = re.search(r'\|\s*编号\s*=\s*([^|\n]+)', wikitext, re.IGNORECASE)
    if id_match:
        ship_data['id'] = id_match.group(1).strip()
    # 解析名称
    name_match = re.search(r'\|\s*名称\s*=\s*([^|\n<]+)', wikitext)
    if name_match:
        ship_data['name'] = name_match.group(1).strip()
    return ship_data

# --- 主程序执行入口 ---

if __name__ == "__main__":
    # 检查并创建输出文件夹
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"已创建输出文件夹: '{OUTPUT_DIR}'")

    all_ships_data = get_all_ship_data()
    
    total_ships = len(all_ships_data)
    print(f"\n准备开始处理全部 {total_ships} 份舰船档案...")
    print("="*50)

    # 遍历所有获取到的舰船数据
    for index, (ship_title, ship_category) in enumerate(all_ships_data):
        # 打印进度条
        print(f"正在处理 ({index + 1}/{total_ships}): {ship_title} (分类: {ship_category}) ...")
        
        # 获取该舰船的原始文本
        wikitext = get_ship_wikitext(ship_title)
        
        if wikitext:
            # 解析文本，提取信息
            ship_data = parse_ship_info_to_dict(wikitext, ship_title)
            
            # 根据分类和解析出的信息，生成文件名
            prefix = CATEGORY_PREFIX_MAP.get(ship_category, "UNKNOWN")
            file_id_safe = re.sub(r'[\\/*?:"<>|]', '_', ship_data['id'])
            file_name_safe = re.sub(r'[\\/*?:"<>|]', '_', ship_data['name'])
            
            filename = f"{prefix}_{file_id_safe}_{file_name_safe}.md"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 将解析出的数据写入文件
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # 直接写入原始的wikitext内容哦~
                    f.write(ship_data['raw_wikitext'])
                print(f"  -> 成功: 档案已保存为: {filename}")
            except Exception as e:
                # 提示信息也变得更通用了呢
                print(f"  -> 错误: 写入文件时失败: {e}")
        else:
            print(f"  -> 错误: 未能获取到 {ship_title} 的原始文本。")
        
        # 每次请求之间礼貌性地停顿1秒
        time.sleep(1)

    print("="*50)
    print("生产任务完成。所有舰船档案均已处理完毕。")

