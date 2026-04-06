import json
import sys
import os
from pathlib import Path
from typing import Any, List
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

sys.path.append(str(Path(__file__).parent.parent))

from logger import info, debug

class BaseAgent:
    
    def __init__(self, llm_client: ChatOpenAI, sys_prompt: str, tools: List[Any], max_loop: int = 20):
        self.tools = tools
        self.sys_prompt = sys_prompt
        self.max_loop = max_loop

        # 创建工具名称到函数的映射
        self.tool_map = {
            tool.name: tool for tool in self.tools
        }
        # 绑定工具到LLM
        self.llm_client = llm_client.bind_tools(self.tools)
        self.messages: List[Any] = [
            SystemMessage(content=self.sys_prompt),
        ]
        
    def before_llm_call(self, messages: List[Any]):
        pass

    def after_tool_call(self, messages: List[Any], tool_calls: List[Any]):
        pass
        
    def __loop(self, messages: List[Any]) -> str | None:
        self.before_llm_call(messages)
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
                messages.append(AIMessage(content=llm_response.content))
                return llm_response.content # type: ignore
            else:
                # 将助手的响应添加到消息历史
                assistant_message = AIMessage(
                    content=llm_response.content,
                    tool_calls=tool_calls
                )
                messages.append(assistant_message)
                # 执行工具调用并收集结果
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    tool_call_id = tool_call.get("id", "")
                    info(f"Executing tool: {tool_name} with args: {tool_args}")                        
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
                self.after_tool_call(messages, tool_calls)
                return None
        except Exception as e:
            info(f"Error in agent loop: {e}")
            return None

    def run(self, prompt: str) -> str:
        self.messages.append(HumanMessage(content=prompt))
        if self.max_loop <= 0:
            while True:
                response = self.__loop(self.messages)
                if response:
                    return response
        else:
            for _ in range(self.max_loop):
                response = self.__loop(self.messages)
                if response:
                    return response
        return "Error: Max loop reached without final answer"
        
if __name__ == "__main__":
    user_input = "列出当前文件夹下的文件, 然后再创建一个叫 debug 的文件夹"
    llm_client = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "glm-4.7-flash"),
        openai_api_key=os.getenv("ZHIPUAI_API_KEY", "your-zhipuai-api-key"), # type: ignore
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/", # type: ignore
    )
    from tools.todo import list_todo, update_todo
    from tools.file import read_file, update_file, write_file
    from tools.exec import exec
    agent_instance = BaseAgent(llm_client, sys_prompt="""
你的角色是一名人工智能助手.
你的任务是先理解用户需求, 使用update_todo和list_todo工具, 通过待办列表的方式进行任务规划.
然后从待办列表中选择一个任务进行执行, 执行完成后更新任务状态, 直到所有任务都完成为止.
严禁直接未经规划直接实现用户需求.
""", tools=[
    list_todo,
    update_todo,
    read_file,
    update_file,
    write_file,
    exec
])
    final_response = agent_instance.run(user_input)
    info(f"Final Response: {final_response}")