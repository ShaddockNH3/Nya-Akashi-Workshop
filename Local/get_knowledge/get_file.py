import os
import re
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- 【核心配置】任务清单 & 输出目录 ---
# 将您提供的所有URL都放在这里！
URL_LIST = [
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E9%99%A8%E7%9F%B3%E4%BA%8B%E4%BB%B6",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E8%83%BD%E6%BA%90%E9%9D%A9%E5%91%BD",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%A7%91%E6%8A%80%E4%B8%8E%E7%94%9F%E6%B4%BB",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%94%9F%E6%B4%BB%E7%9A%84%E5%8F%98%E9%9D%A9",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E9%AD%94%E6%96%B9%E5%86%9B%E7%94%A8%E5%8C%96",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E9%AD%94%E6%96%B9%E5%86%9B%E7%94%A8%E5%8C%96II",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E3%80%8C%E5%BE%AE%E5%85%89%E3%80%8D%E8%AE%A1%E5%88%92",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E9%AD%94%E6%96%B9%E7%9A%84%E5%A5%A5%E7%A7%98",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E4%BB%A3%E5%8F%B7%EF%BC%9ACODEG",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%86%9B%E5%A4%87%E7%AB%9E%E8%B5%9B",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E6%9C%BA%E5%AF%86%E8%AE%B0%E5%BD%95I",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%A4%A7%E5%AD%A6%E6%97%B6%E4%BB%A3",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%86%8D%E6%AC%A1%E4%BA%A4%E6%B1%87%E7%9A%84%E7%BA%A2%E7%BA%BF",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%8E%B0%E5%9C%A8%E4%B8%8E%E6%9C%AA%E6%9D%A5",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%BC%82%E5%B8%B8%E5%86%B2%E5%87%BB%E4%BA%8B%E4%BB%B6I",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%BC%82%E5%B8%B8%E5%86%B2%E5%87%BB%E4%BA%8B%E4%BB%B6II",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E5%8D%B1%E6%9C%BA%E5%9B%9B%E4%BC%8F",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%90%86%E6%9F%A5%E5%BE%B7%E4%BA%8B%E4%BB%B6I",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%90%86%E6%9F%A5%E5%BE%B7%E4%BA%8B%E4%BB%B6II",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%90%86%E6%9F%A5%E5%BE%B7%E4%BA%8B%E4%BB%B6III",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%90%86%E6%9F%A5%E5%BE%B7%E4%BA%8B%E4%BB%B6IV",
    "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88/%E7%90%86%E6%9F%A5%E5%BE%B7%E6%A1%A3%E6%A1%88I"
]

OUTPUT_DIR = os.path.join("activity_stories_production", "File") # 所有文件都保存到这个子目录
DRIVER_PATH = './chromedriver.exe'

def fetch_and_parse_archive_page(driver, url):
    """
    【升级版】专门为“档案”类页面优化的解析器。
    它能更准确地处理这类页面的通用结构。
    """
    print(f"  - 正在访问URL: {url}")
    try:
        driver.get(url)
        # 等待核心内容区域加载，确保JS渲染完成
        wait = WebDriverWait(driver, 20)
        content_element = wait.until(
            EC.presence_of_element_located((By.ID, 'mw-content-text'))
        )
        
        # 使用BeautifulSoup进行精细解析
        html_content = content_element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'lxml')
        
        parser_output = soup.find('div', class_='mw-parser-output')
        if not parser_output:
            print("    -> 错误: 页面结构异常，未找到 'mw-parser-output' 容器。")
            return None

        markdown_output = []
        
        # 1. 优先从页面的H1标题获取主标题 (Bwiki正文标题通常是H1)
        main_title_tag = soup.find('h1', id='firstHeading')
        story_title = url.split('/')[-1] # 默认标题
        if main_title_tag:
            story_title = main_title_tag.get_text(strip=True)
        markdown_output.append(f"# {story_title}\n")

        # 2. 遍历所有直接子元素，进行结构化处理
        for element in parser_output.find_all(['h2', 'h3', 'p', 'div', 'ul', 'ol', 'table']):
            # 跳过目录和一些无用div
            if element.get('id') == 'toc' or (element.name == 'div' and not element.get_text(strip=True)):
                continue

            # A. H2或H3标题，都视为新的二级章节
            if element.name in ['h2', 'h3'] and element.find('span', class_='mw-headline'):
                section_title = element.get_text(strip=True).replace('[编辑]', '').strip()
                markdown_output.append(f"## {section_title}\n")
            
            # B. 对于普通的段落、列表、表格等内容
            elif element.name in ['p', 'ul', 'ol', 'table'] and element.get_text(strip=True):
                 # 直接添加元素的文本内容，并做一些清理
                 text_content = element.get_text(separator='\\n').strip()
                 # 避免重复添加只有换行符的内容
                 if text_content:
                     markdown_output.append(text_content + "\n")
            
            # C. 特别处理对话类的div（这是Bwiki常用格式）
            elif element.name == 'div' and 'panel-body' in str(element):
                # 提取panel-body内的文本，通常是对话内容
                body_text = element.get_text(separator='\\n', strip=True)
                if body_text:
                    markdown_output.append(body_text + "\n")


        # 清理空行，让格式更美观
        final_text = "\n".join(line for line in markdown_output if line.strip())
        return final_text

    except Exception:
        print(f"    -> 严重错误：处理页面 {url} 时发生崩溃。")
        print(f"       详细信息: {traceback.format_exc()}")
        return None

# --- 主程序执行入口 ---
if __name__ == "__main__":
    # 确保输出目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"[初始化] 已确保输出目录存在: '{OUTPUT_DIR}'")

    # 初始化WebDriver
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    
    total_urls = len(URL_LIST)
    print(f"\n[任务开始] 准备处理 {total_urls} 个档案链接...")
    print("=" * 70)
    
    try:
        for index, url in enumerate(URL_LIST):
            sequence_num = index + 1
            print(f"\n[处理中 {sequence_num}/{total_urls}]")
            
            # 核心抓取与解析步骤
            markdown_content = fetch_and_parse_archive_page(driver, url)
            
            if markdown_content:
                # 从解析内容中获取标题作为文件名
                first_line = markdown_content.split('\n')[0]
                if first_line.startswith('# '):
                    file_title = first_line[2:].strip()
                else:
                    # 如果解析失败，则使用URL的最后部分作为后备文件名
                    file_title = url.split('/')[-1]

                # 清理文件名中的非法字符
                safe_title = re.sub(r'[\\/*?:"<>|]', '_', file_title)
                # 使用序号确保文件顺序
                filename = f"{sequence_num:03d}_{safe_title}.md"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    print(f"    -> [成功] 已保存至: '{filename}'")
                except Exception as e:
                    print(f"    -> [错误] 写入文件失败，原因: {e}")
            else:
                 print(f"    -> [失败] 未能从该URL获取有效内容，已跳过。")
            
            # 每次抓取后暂停一下，模仿人类操作，避免被网站屏蔽
            time.sleep(2)

    finally:
        print("\n" + "=" * 70)
        print("[任务结束] 所有链接已处理完毕，正在关闭浏览器...")
        driver.quit()

