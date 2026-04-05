from typing import Dict, Iterator, List, Any, Callable
from ollama import ChatResponse, Client

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from llm.llm_response import LLMResponse
from logger import info, debug

def generate_ollama(model: str, messages: List[Dict[str, Any]], tools: List[Callable[[Any], Any]] | None) -> LLMResponse:
    client: Client = Client()
    chat_response: Iterator[ChatResponse] = client.chat(
        model, 
        stream=True, 
        messages=messages, 
        tools=tools, 
        think=True,
        options={
            "temperature": 0.7,
            "top_p": 0.7,
        }
    )
    response = ""
    thinking = ""
    total_duration = 0.0
    input_token = 0
    cached_token = 0
    output_token = 0
    tool_calls: List[Dict[str, Any]] = []
    for chunk in chat_response:
        if chunk.message.thinking:
            thinking += chunk.message.thinking
        if chunk.message.content:
            response += chunk.message.content
        if chunk.message.tool_calls:
            for tool in chunk.message.tool_calls:
                tool_calls.append({
                    "name": tool.function.name,
                    "arguments": tool.function.arguments
                })
        if chunk.done:
            total_duration = chunk.total_duration or 0.0
            input_token = chunk.prompt_eval_count or 0
            output_token = chunk.eval_count or 0

    return LLMResponse(response, thinking, total_duration, input_token, cached_token, output_token, tool_calls)

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "和我打个招呼吧"}
    ]
    tools: List[Callable[[Any], Any]] = []
    def hello_tool(content: str) -> str:
        """
        打招呼专用工具
        Args:
            content (str): 用户输入的内容
        Returns:
            str: 打招呼的结果
        """
        debug(f"Hello tool called with content: {content}")
        return f"Hello, you said: {content}"
    tools.append(hello_tool)
    result = generate_ollama("qwen3.5:4b", messages, tools)
    info(f"Ollama response: \n{result}")