import os
os.environ["LOG_LEVEL"] = "WARNING"  # 设置日志级别为 WARNING

from agent.index import Agent

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
    print("请输入你的需求，输入 '\\q' 退出。\n================================\n")
    while True:
        user_input = input("😊 >> ")
        if user_input.lower() == "\\q":
            print("\nBye~\n")
            break
        agent_instance = Agent()
        final_response = agent_instance.run(user_input)
        print(f"\n🤖 >> {final_response}\n")

if __name__ == "__main__":
    main()
