
sys_prompt = """
[SYSTEM]
你的角色是一个人工智能助手.

你的任务是接收到用户需求, 识别用户意图, 进行任务规划并完成子任务. 
使用看板工具将任务分解成多个子任务, 并标记每个子任务的状态.
严格按照todo, doing, done三个状态进行标记, 必须先标记todo, 执行任务开始时, 标记为doing, 验证结果后才能更新为done.
所有任务都完成后, 才能给出最终的结果.

如果需要调用工具, 返回格式必须是严格的json结构.
{
    "tool_calls": [
        {
            "name": "工具名称1",
            "id": "唯一标识符1",
            "input": {
                "参数1": "参数1的值",
                "参数2": "参数2的值"
            }
        },
        {
            "name": "工具名称2",
            "id": "唯一标识符2",
            "input": {
                "参数1": "参数1的值"
            }
        }
    ]
}

<user>内为用户的输入
<tools>内为可用工具列表
<thinking>内为你之前的思考过程
<tool_calls>内为你之前调用的工具列表
<tool_results>内为你之前调用工具的结果
<reminder>内为提醒内容
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from llm import llm_client
from logger import info, debug
from tools.tools import Tools

class Agent:
    
    def __init__(self):
        self.tools = Tools()
        self.client = llm_client.LLMClient()
    

    def run(self, prompt: str) -> str:
        message = sys_prompt + "\n" + self.tools.describe_tools()  + "\n\n" + f"<user>{prompt}</<user>"
        doing_round = 0
        while True:
            update_kanban = False
            debug(f"Send message to LLM:\n{message}")
            result = self.client.generate(message)
            try:
                debug(f"Raw response from LLM:\n{result}")
                response_json = json.loads(result.response.replace("```json", "").replace("```", ""))
                tool_calls = response_json.get("tool_calls", [])
                if not tool_calls:
                    # 如果没有工具调用，返回最终答案
                    return result.response
                else:
                    thinking = result.thinking
                    info(f"LLM thinking: {thinking}")
                    message += f"\n<thinking>\n{thinking}\n</thinking>"
                    message += f"\n<tool_calls>\n{tool_calls}\n</tool_calls>"
                    tool_results = ["<tool_results>"]
                    for tool_call in tool_calls:
                        debug(f"Tool call: {tool_call}")
                        if tool_call.get("name", "") == "update_kanban":
                            update_kanban = True
                        tool_result = self.tools.call_tool(tool_call.get("name", ""), **tool_call.get("input", {}))
                        tool_results.append(json.dumps({
                            "id": tool_call.get("id", ""),
                            "result": tool_result
                        }, ensure_ascii=False))
                        debug(f"Tool result for '{tool_call.get('id', '')}' '{tool_call.get('name', '')}': {tool_result}")
                    tool_results.append("</tool_results>")
                    message += "\n" + "\n".join(tool_results)
                    if not update_kanban:
                        doing_round += 1
                    if doing_round >= 3:
                        message += "\n<reminder>\n看板状态已经连续3轮没有更新了, 请检查是否正确使用看板工具进行任务分解和状态更新!!\n</reminder>"
            except json.JSONDecodeError:
                # 如果响应不是 JSON，直接返回原始响应
                return result.response
        
if __name__ == "__main__":
    user_input = "在当前目录下, 创建一个叫 debug 的文件夹"
    agent_instance = Agent()
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")