import os
import json
import sys

# 导入我们的中央导航系统
PROJECT_ROOT = "/root/autodl-tmp/Akashi"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
try:
    from graph_rag import config
except ImportError:
    print("[致命错误] 无法从 'graph_rag' 模块导入 config！")
    exit()

def create_character_index():
    """
    这个脚本将执行您的天才战术！
    它会扫描 ships 文件夹，创建一个 Character_Name -> File_Path 的“对应表”，
    并将其保存为一个简单、可靠的 JSON 文件。
    这就是我们的『皇家档案馆』索引！
    """
    print("--- [战术变更] 开始建造『皇家档案馆』索引... ---")
    
    ships_folder_path = os.path.join(config.PROJECT_BASE_PATH, "clean_knowledge", "ships")
    index_file_path = os.path.join(config.PROJECT_BASE_PATH, "data", "character_index.json")
    
    if not os.path.isdir(ships_folder_path):
        print(f"[错误] 找不到角色档案文件夹: {ships_folder_path}")
        return

    character_index = {}
    
    print(f" -> 正在扫描文件夹: {ships_folder_path}")
    file_list = os.listdir(ships_folder_path)
    
    for file_name in file_list:
        if file_name.endswith('.md'):
            # 使用我们已经验证过的、最可靠的方法提取角色名
            character_name = file_name.split('_')[-1].replace('.md', '')
            full_file_path = os.path.join(ships_folder_path, file_name)
            
            # 写入“对应表”
            character_index[character_name] = full_file_path
            
    if character_index:
        print(f" -> 成功为 {len(character_index)} 位舰船创建了索引。")
        try:
            with open(index_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_index, f, ensure_ascii=False, indent=4)
            print(f"🎉 『皇家档案馆』索引建造完毕，已保存至: {index_file_path}")
        except Exception as e:
            print(f"[错误] 保存索引文件失败: {e}")
    else:
        print("[警告] 未在 ships 文件夹中找到任何 .md 文件。")

if __name__ == "__main__":
    create_character_index()
