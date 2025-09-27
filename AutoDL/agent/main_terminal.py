# 文件路径: agent/main_terminal.py (V8.2 终极版)

import sys
import os

# --- 【“就地觉醒”核心代码】 ---
# 无论如何，我们都要确保项目根目录在Python的认知范围内。
# 1. 获取当前文件(main_terminal.py)所在的目录: .../Akashi/agent
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. 获取上一级目录，也就是我们的项目根目录: .../Akashi
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
# 3. 如果根目录不在Python的搜索路径中，就把它加进去！
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --- 路径修正完毕，现在可以安全地进行任何导入了 ---

# --- 颜色代码 (不变) ---
class Colors:
    GREEN = '\033[92m'; CYAN = '\033[96m'; YELLOW = '\033[93m'
    ENDC = '\03a[0m'; BOLD = '\033[1m'

# 现在，我们可以自信地从“根目录”的角度来导入模块
from langchain_core.messages import HumanMessage, AIMessage
from agent.akashi_agent import AkashiAgent

def run_terminal():
    """
    运行“宗师级工匠-茗”的纯终端交互模式。
    """
    print("\n" + "="*70)
    print(f"{Colors.CYAN}{Colors.BOLD}宗师级工匠-茗 V8.2 (就地部署版) 已启动！{Colors.ENDC}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录已锁定: {PROJECT_ROOT}")

    agent = AkashiAgent() # 初始化工匠

    print("\n" + "="*70 + f"\n{Colors.GREEN}初始化完成！现在您可以开始与茗喵对话了。{Colors.ENDC}")
    print(f"输入 {Colors.YELLOW}'exit'{Colors.ENDC} 或 {Colors.YELLOW}'quit'{Colors.ENDC} 来结束对话。\n" + "="*70)
    
    conversation_history = []
    while True:
        try:
            user_input = input(f"\n{Colors.GREEN}{Colors.BOLD}指挥官大人 > {Colors.ENDC}")
            if user_input.lower() in ['exit', 'quit', '再见']:
                print(f"\n{Colors.CYAN}任务结束！茗喵要去清点这次行动的战利品啦~{Colors.ENDC}")
                break

            response = agent.invoke(user_input, conversation_history)
            
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response))
            
            print(f"\n{Colors.CYAN}{Colors.BOLD}茗喵：{Colors.ENDC}\n{Colors.CYAN}{response}{Colors.ENDC}")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}收到强制中断指令！茗喵退下了...{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.YELLOW}[运行时错误] {e}{Colors.ENDC}\n  -> 对话已重置。{Colors.ENDC}")
            conversation_history = []

if __name__ == "__main__":
    run_terminal()
