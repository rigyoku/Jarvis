import sys
import os
from pathlib import Path
from typing import Callable
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from logger import info
from tools.file import read_file, update_file, write_file
from tools.exec import exec
from skills import get_metadata, get_skill_content

class Agent:
    
    def __init__(self, llm_client_factory: Callable[[], ChatOpenAI | ChatGoogleGenerativeAI]):
        """
        初始化Agent
        Args:
            llm_client_factory: 创建LLM客户端的工厂函数,确保每个子Agent有独立的客户端实例
        """
        self.llm_client_factory = llm_client_factory
        self.tools = [
            read_file,
            update_file,
            write_file,
            exec,
        ]

        @tool
        def run_sub_agent(prompt: str) -> str:
            """
            运行子Agent来处理复杂任务
            Args:
                prompt: 子Agent的任务描述
            Returns:
                子Agent的输出结果
            """
            # 为子Agent创建独立的客户端实例
            sub_client = self.llm_client_factory()
            return BaseAgent(sub_client, f"""
你的角色是执行具体任务的子Agent. 根据主Agent的指示, 你将执行具体的任务, 并将任务结果汇总返回给主Agent.
可用的技能如下:
{get_metadata()}
""", [
            read_file,
            update_file,
            write_file,
            exec,
            get_skill_content,
        ]).run(prompt)

        # 为主Agent创建独立的客户端实例
        main_client = self.llm_client_factory()
        self.main_agent = BaseAgent(main_client, f"""
你的角色是一名人工智能助手. 你的任务是理解用户需求, 并根据需求委派子Agent来执行具体任务.
可用的技能如下:
{get_metadata()}
""", [
            run_sub_agent,
        ], max_loop=40)
    

    def run(self, prompt: str) -> str:
        return self.main_agent.run(prompt)
        
if __name__ == "__main__":
    user_input = "当前工程的主要技术栈是什么"
    
    def create_llm_client():
        return ChatOpenAI(
            model=os.getenv("LLM_MODEL", "glm-4.7-flash"),
            openai_api_key=os.getenv("LLM_API_KEY", "your-api-key"), # type: ignore
            openai_api_base=os.getenv("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4/"), # type: ignore
        )
    
    agent_instance = Agent(create_llm_client)
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")