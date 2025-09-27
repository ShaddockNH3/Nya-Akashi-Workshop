import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- 全局配置 ---
MAIN_PAGE_URL = "https://wiki.biligame.com/blhx/%E7%A2%A7%E8%93%9D%E5%9B%9E%E5%BF%86%E5%BD%95%E6%96%87%E5%AD%97%E7%89%88"
OUTPUT_DIR = "activity_stories_production"
OUTPUT_SUBDIR_CHAR = os.path.join(OUTPUT_DIR, "Character")
# WebDriver的路径，如果chromedriver.exe和脚本在同一个文件夹，这样写就行
DRIVER_PATH = './chromedriver.exe'

def get_character_story_urls(driver):
    """
    第一步：驾驶浏览器访问主目录，找出所有角色剧情的URL。
    """
    print("阶段一：正在启动浏览器，扫描角色剧情URL列表...")
    driver.get(MAIN_PAGE_URL)
    
    story_urls = []
    try:
        # 等待剧情容器加载出来，最多等15秒
        wait = WebDriverWait(driver, 15)
        # 使用CSS选择器精确定位
        story_containers = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Flour[data-particle-0="角色"]'))
        )
        
        for container in story_containers:
            # 在每个容器内部寻找<a>标签
            link_tag = container.find_element(By.TAG_NAME, 'a')
            story_urls.append(link_tag.get_attribute('href'))

    except Exception as e:
        print(f"  -> 错误：在主目录页扫描失败，原因: {e}")
        return []

    # 跳过第一个图标链接
    if story_urls:
        print(f"  -> 扫描成功！发现 {len(story_urls) - 1} 个角色剧情URL。")
        return story_urls[1:]
    else:
        print("  -> 扫描失败，未找到任何角色剧情条目。")
        return []

def fetch_and_parse_story_page_with_selenium(driver, url):
    """
    第二步：驾驶浏览器访问单个剧情页面，提取并格式化内容。
    """
    print(f"  - 正在访问URL: {url}")
    driver.get(url)
    
    try:
        # 等待核心内容区域加载出来
        wait = WebDriverWait(driver, 15)
        content_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mw-parser-output'))
        )
        
        # 获取核心内容区域的HTML，然后交给BeautifulSoup处理，效率最高！
        html_content = content_element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'lxml')
        
        # (后续的解析逻辑和之前完全一样)
        markdown_output = []
        story_title = url.split('/')[-1] # 从URL获取默认标题
        main_title_tag = soup.find('h2')
        if main_title_tag and main_title_tag.find('span', class_='mw-headline'):
            story_title = main_title_tag.find('span', class_='mw-headline').get_text(strip=True)
        markdown_output.append(f"# {story_title}\n")
        
        panels = soup.find_all('div', class_='panel-primary')
        for panel in panels:
            heading = panel.find('div', class_='panel-heading')
            section_title = "未知章节"
            if heading and heading.find('span', class_='panel-title'):
                section_title = heading.find('span', class_='panel-title').get_text(strip=True)
            markdown_output.append(f"## {section_title}\n")
            
            body = panel.find('div', class_='panel-body')
            if body:
                content_html = ''.join(str(child) for child in body.contents).strip()
                markdown_output.append(f"{content_html}\n")
                
        return "\n".join(markdown_output)

    except Exception as e:
        print(f"    -> 错误：处理页面 {url} 时失败，原因: {e}")
        return None

# --- 主程序执行入口 ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_SUBDIR_CHAR):
        os.makedirs(OUTPUT_SUBDIR_CHAR)
    print(f"已确保输出目录存在: '{OUTPUT_SUBDIR_CHAR}'")
    
    # 初始化WebDriver服务
    service = Service(executable_path=DRIVER_PATH)
    # 启动浏览器实例
    driver = webdriver.Chrome(service=service)
    
    try:
        character_urls = get_character_story_urls(driver)
        
        if character_urls:
            total = len(character_urls)
            print(f"\n阶段二：准备开始抓取并格式化全部 {total} 份角色剧情...")
            print("="*60)
            
            for index, url in enumerate(character_urls):
                sequence_num = index + 1
                
                # 从URL中提取标题用于文件名
                title = url.split('/')[-1]
                
                markdown_content = fetch_and_parse_story_page_with_selenium(driver, url)
                
                if markdown_content:
                    filename_prefix = f"{sequence_num:03d}"
                    filename_title = re.sub(r'[\\/*?:"<>|]', '_', title)
                    filename = f"{filename_prefix}_{filename_title}.md"
                    filepath = os.path.join(OUTPUT_SUBDIR_CHAR, filename)
                    
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        print(f"    -> 成功: 已保存至 'Character' 目录: {filename}")
                    except Exception as e:
                        print(f"    -> 错误: 写入文件失败，原因: {e}")
                
                # 即使是浏览器操作，也最好有停顿，避免过快操作导致问题
                time.sleep(1)

            print("="*60)
            print("所有角色剧情已处理完毕！")
            
    finally:
        # 无论成功还是失败，最后一定要关闭浏览器！
        print("\n任务结束，正在关闭浏览器...")
        driver.quit()

