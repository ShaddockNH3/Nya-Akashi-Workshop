import os
import re
import json

INPUT_DIR = "ships" 

OUTPUT_FILE = "censored_name_to_real_name.json"

# ---------------------------------------------------

def create_mapping():
    """
    遍历指定文件夹中的所有 .md 文件,
    提取和谐名与姓名,并生成一个 JSON 映射表。
    """
    mapping_dict = {}
    print(f"进入 '{INPUT_DIR}' ")

    if not os.path.exists(INPUT_DIR):
        print(f"找不到 '{INPUT_DIR}' 文件夹，请确认路径正确")
        return

    # 开始一本一本地翻阅档案
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(INPUT_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    # 为了效率，只读前5行
                    head_content = "".join([next(f) for _ in range(5)])
            except StopIteration:
                # 如果文件行数不足5行，就读取所有内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    head_content = f.read()
            except Exception as e:
                print(f"  -> 读取文件 {filename} 时遇到一点小麻烦: {e}")
                continue

            # 使用“高精度扫描仪”(正则表达式)来寻找信息
            # 查找姓名，例如: "### 姓名：水无濑" -> 捕获 "水无濑"
            name_match = re.search(r"### 姓名：(.*?)\n", head_content)
            # 查找和谐名，例如: "* **和谐名：** 鼯" -> 捕获 "鼯"
            censored_match = re.search(r"\* \*\*和谐名：\*\* (.*?)\n", head_content)

            # 必须同时找到姓名与和谐名，才进行记录！
            if name_match and censored_match:
                # .group(1) 是提取括号里捕获的内容, .strip() 是去掉前后多余的空格
                real_name = name_match.group(1).strip()
                censored_name = censored_match.group(1).strip()

                if real_name and censored_name:
                    # 在名册上记下一笔！
                    mapping_dict[censored_name] = real_name
                    print(f"  -> 找到一对映射: '{censored_name}' -> '{real_name}'")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 可以保证中文正常显示
            # indent=4 是为了让JSON文件格式变得漂亮，方便人阅读
            json.dump(mapping_dict, f, ensure_ascii=False, indent=4)
        print(f"\n文件保存在: '{OUTPUT_FILE}'")
        print(f"总共记录了 {len(mapping_dict)} 对名字映射！")
    except Exception as e:
        print(f"\n保存名册的时候失败了: {e}")

# --- 主程序入口 ---
if __name__ == "__main__":
    create_mapping()

