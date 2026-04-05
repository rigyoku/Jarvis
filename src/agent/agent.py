
sys_prompt = """
你的角色是一名人工智能助手.
你的任务是先理解用户需求, 使用update_todo和list_todo工具, 通过待办列表的方式进行任务规划.
然后从待办列表中选择一个任务进行执行, 执行完成后更新任务状态, 直到所有任务都完成为止.
严禁直接未经规划直接实现用户需求.
"""

import json
import sys
import os
from pathlib import Path
from typing import Any, List
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

sys.path.append(str(Path(__file__).parent.parent))

from logger import info, debug
from tools.todo import list_todo, update_todo
from tools.file import read_file, update_file, write_file
from tools.exec import exec

class Agent:
    
    def __init__(self, llm_client: ChatOpenAI):
        self.tools = [
            list_todo,
            update_todo,
            read_file,
            update_file,
            write_file,
            exec,
        ]
        # 创建工具名称到函数的映射
        self.tool_map = {
            tool.name: tool for tool in self.tools
        }
        # 绑定工具到LLM
        self.llm_client = llm_client.bind_tools(self.tools)
    

    def run(self, prompt: str) -> str:
        # 初始化消息历史
        messages: List[Any] = [
            SystemMessage(content=sys_prompt),
            HumanMessage(content=prompt)
        ]
        doing_round = 0
        while True:
            update_todo = False
            debug(f"""

Sending messages to LLM

===============>
{"\n".join(str(message) for message in messages)}
<===============

""")
            llm_response = self.llm_client.invoke(messages)
            try:
                debug(f"""

Raw response from LLM

===============>
{llm_response}
<===============

""")
                tool_calls = llm_response.tool_calls
                
                if not tool_calls:
                    # 如果没有工具调用，返回最终答案
                    return llm_response.content # type: ignore
                else:
                    # thinking = result.thinking
                    # info(f"LLM thinking: {thinking}")
                    
                    # 将助手的响应添加到消息历史
                    assistant_message = AIMessage(
                        content=llm_response.content,
                        tool_calls=tool_calls
                    )
                    # if thinking:
                    #     assistant_message["thinking"] = thinking
                    messages.append(assistant_message)
                    
                    # 执行工具调用并收集结果
                    for tool_call in tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call.get("args", {})
                        tool_call_id = tool_call.get("id", "")
                        
                        info(f"Executing tool: {tool_name} with args: {tool_args}")
                        
                        # 检查是否是update_todo或list_todo
                        if tool_name in ["update_todo", "list_todo"]:
                            update_todo = True
                        
                        # 执行工具
                        try:
                            if tool_name in self.tool_map:
                                tool_func = self.tool_map[tool_name]
                                tool_result = tool_func.invoke(tool_args)
                                result_content = json.dumps(tool_result, ensure_ascii=False) if not isinstance(tool_result, str) else tool_result
                            else:
                                result_content = f"Error: Tool '{tool_name}' not found"
                                info(f"Tool not found: {tool_name}")
                        except Exception as e:
                            result_content = f"Error executing tool '{tool_name}': {str(e)}"
                            info(f"Error executing tool {tool_name}: {e}")
                        
                        # 将工具结果作为ToolMessage添加到历史
                        messages.append(ToolMessage(
                            content=result_content,
                            tool_call_id=tool_call_id
                        ))
                    
                    if not update_todo:
                        doing_round += 1
                    else:
                        doing_round = 0
                        
                    if doing_round >= 3:
                        messages.append(AIMessage(content="待办列表状态已经连续3轮没有更新了, 请检查是否正确使用待办列表工具进行任务分解和状态更新!!"))
                        doing_round = 0
                        
            except Exception as e:
                info(f"Error in agent loop: {e}")
        
if __name__ == "__main__":
    user_input = "列出当前文件夹下的文件, 然后再创建一个叫 debug 的文件夹"
    llm_client = ChatOpenAI(
        model="glm-4.7-flash",
        openai_api_key=os.getenv("ZHIPUAI_API_KEY", "your-zhipuai-api-key"), # type: ignore
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/", # type: ignore
    )
    agent_instance = Agent(llm_client)
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")