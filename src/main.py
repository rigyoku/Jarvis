import os
os.environ["LOG_LEVEL"] = "WARNING"  # 设置日志级别为 WARNING
from langchain_openai import ChatOpenAI

from agent.agent import Agent

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
    llm_client = ChatOpenAI(
        model="glm-5",
        openai_api_key=os.getenv("ZHIPUAI_API_KEY", "your-zhipuai-api-key"), # type: ignore
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/", # type: ignore
    )
    agent_instance = Agent(llm_client)
    print("请输入你的需求，输入 '\\q' 退出。\n================================\n")
    while True:
        user_input = input("😊 >> ")
        if user_input.lower() == "\\q":
            print("\nBye~\n")
            break
        final_response = agent_instance.run(user_input)
        print(f"\n🤖 >> {final_response}\n")

if __name__ == "__main__":
    main()
