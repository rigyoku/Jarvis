
sys_prompt = """
[SYSTEM]
你的角色是一个人工智能助手, 你的任务是识别用户的意图, 并按需调用工具, 直到完成用户的需求.
如果需要调用工具, 返回格式必须是严格的json结构
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
        while True:
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
                        tool_result = self.tools.call_tool(tool_call.get("name", ""), **tool_call.get("input", {}))
                        tool_results.append(json.dumps({
                            "id": tool_call.get("id", ""),
                            "result": tool_result
                        }, ensure_ascii=False))
                        debug(f"Tool result for '{tool_call.get('id', '')}' '{tool_call.get('name', '')}': {tool_result}")
                    tool_results.append("</tool_results>")
                    message += "\n" + "\n".join(tool_results)
            except json.JSONDecodeError:
                # 如果响应不是 JSON，直接返回原始响应
                return result.response
        
if __name__ == "__main__":
    user_input = "在当前目录下, 创建一个叫 debug 的文件夹"
    agent_instance = Agent()
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")