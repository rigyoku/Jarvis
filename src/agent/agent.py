
sys_prompt = """
你的角色是一名人工智能助手.
你的任务是理解用户需求, 使用update_todo和list_todo工具, 通过待办列表的方式进行任务规划.
然后从待办列表中选择一个任务进行执行, 执行完成后更新任务状态, 直到所有任务都完成为止.
role为reminder时, 内容为对助手的提醒, 需要特别注意
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.append(str(Path(__file__).parent.parent))

from llm import llm_client
from logger import info, debug
from tools.tools import Tools

class Agent:
    
    def __init__(self):
        self.tools = Tools()
        self.client = llm_client.LLMClient()
    

    def run(self, prompt: str) -> str:
        # 初始化消息历史
        messages = [
            {
                "role": "system",
                "content": sys_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
        injected_tools = False
        doing_round = 0
        while True:
            update_todo = False
            debug(f"""

Sending messages to LLM

===============>
{"\n".join([json.dumps(message, ensure_ascii=False) for message in messages])}
<===============

""")
            if not injected_tools:
                result = self.client.generate(messages, Tools().get_tools())
                injected_tools = True
            else:
                result = self.client.generate(messages)
            try:
                debug(f"""

Raw response from LLM

===============>
{result}
<===============

""")
                tool_calls = result.tool_calls
                
                if not tool_calls:
                    # 如果没有工具调用，返回最终答案
                    return result.response
                else:
                    # thinking = result.thinking
                    # info(f"LLM thinking: {thinking}")
                    
                    # 将助手的响应添加到消息历史
                    assistant_message = {
                        "role": "assistant",
                        "content": result.response
                    }
                    # if thinking:
                    #     assistant_message["thinking"] = thinking
                    messages.append(assistant_message)
                    
                    # 执行工具调用并收集结果
                    tool_results: List[Dict[str, Any]] = []
                    for tool_call in tool_calls:
                        if tool_call.get("name", "") == "update_todo":
                            update_todo = True
                        tool_result = self.tools.call_tool(tool_call.get("name", ""), **tool_call.get("arguments", {}))
                        tool_results.append({
                            "name": tool_call.get("name", ""),
                            "result": tool_result
                        })
                    
                    # 将工具结果作为用户消息添加到历史
                    tool_results_content = "\n".join([
                        json.dumps(tr, ensure_ascii=False) for tr in tool_results
                    ])
                    
                    messages.append({
                        "role": "tool",
                        "content": tool_results_content
                    })
                    
                    if not update_todo:
                        doing_round += 1
                    else:
                        doing_round = 0
                        
                    if doing_round >= 3:
                        messages.append({
                            "role": "reminder",
                            "content": "\n待办列表状态已经连续3轮没有更新了, 请检查是否正确使用待办列表工具进行任务分解和状态更新!!\n"
                        })
                        doing_round = 0
                        
            except Exception:
                # 直接返回原始响应
                return result.response
        
if __name__ == "__main__":
    user_input = "列出当前文件夹下的文件, 然后再创建一个叫 debug 的文件夹"
    agent_instance = Agent()
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")