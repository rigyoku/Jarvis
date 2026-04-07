import os
os.environ["LOG_LEVEL"] = "WARNING"  # 设置日志级别为 WARNING
from langchain_openai import ChatOpenAI

from agents.agent import Agent
from logger import debug

try:
    import readline
    # #143 UTF-8 backspace fix for macOS libedit
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
    readline.parse_and_bind('set enable-meta-keybindings on')
except ImportError:
    pass

def main():
    debug(f"""
Starting Jarvis Agent...
LLM_MODEL: {os.getenv("LLM_MODEL", "glm-4.7-flash")}
LLM_API_KEY: {'XXXX' if os.getenv("LLM_API_KEY") else 'Not Set'}
LLM_API_BASE: {os.getenv("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/")}
""")
    
    # 创建LLM客户端工厂函数
    def create_llm_client():
        if os.getenv("LLM_MODEL", "").startswith("gemini"):
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=os.getenv("LLM_MODEL", "gemini-3.1-flash-lite-preview"),
                google_api_key=os.getenv("LLM_API_KEY", "your-api-key"), # type: ignore
            )
        else:
            return ChatOpenAI(
                model=os.getenv("LLM_MODEL", "glm-4.7-flash"),
                openai_api_key=os.getenv("LLM_API_KEY", "your-api-key"), # type: ignore
                openai_api_base=os.getenv("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/"), # type: ignore
            )
    
    agent_instance = Agent(create_llm_client)
    print("请输入你的需求,输入 '\\q' 退出.\n================================\n")
    while True:
        user_input = input("😊 >> ")
        if user_input.lower() == "\\q":
            print("\nBye~\n")
            break
        final_response = agent_instance.run(user_input)
        print(f"\n🤖 >> {final_response}\n")

if __name__ == "__main__":
    main()
