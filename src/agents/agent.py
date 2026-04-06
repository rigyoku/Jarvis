import sys
import os
from pathlib import Path
from langchain.tools import tool
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from logger import info
from tools.file import read_file, update_file, write_file
from tools.exec import exec
class Agent:
    
    def __init__(self, llm_client: ChatOpenAI):
        self.tools = [
            read_file,
            update_file,
            write_file,
            exec,
        ]
        self.sub_agent = BaseAgent(llm_client.model_copy(), """
你的角色是执行具体任务的子Agent. 根据主Agent的指示, 你将执行具体的任务, 并将任务结果汇总返回给主Agent.
""", [
            read_file,
            update_file,
            write_file,
            exec,
        ])
        
        @tool
        def run_sub_agent(prompt: str) -> str:
            """
            运行子Agent来处理复杂任务
            Args:
                prompt: 子Agent的任务描述
            Returns:
                子Agent的输出结果
            """
            return self.sub_agent.run(prompt)

        self.main_agent = BaseAgent(llm_client.model_copy(), """
你的角色是一名人工智能助手. 你的任务是理解用户需求, 并根据需求委派子Agent来执行具体任务.
""", [
            run_sub_agent,
        ], max_loop=40)
    

    def run(self, prompt: str) -> str:
        return self.main_agent.run(prompt)
        
if __name__ == "__main__":
    user_input = "当前工程的主要技术栈是什么"
    llm_client = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "glm-4.7-flash"),
        openai_api_key=os.getenv("ZHIPUAI_API_KEY", "your-zhipuai-api-key"), # type: ignore
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/", # type: ignore
    )
    agent_instance = Agent(llm_client)
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")