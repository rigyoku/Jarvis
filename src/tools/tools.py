import os
import glob
import importlib.util
from typing import Callable, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator
from logger import info, debug, error

@decorator.singleton
class Tools:

    __tools: list[Callable[..., Any]] = []

    def __init__(self) -> None:
        self.__register_tools()

    def __register_tools(self) -> None:
        """
        扫描当前文件夹下的所有python文件, 将其中定义的工具函数注册到工具列表中
        工具函数必须使用 @tool 装饰器进行标记
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tool_files = glob.glob(os.path.join(current_dir, "*.py"))
        
        for tool_file in tool_files:
            module_name = os.path.splitext(os.path.basename(tool_file))[0]
            spec = importlib.util.spec_from_file_location(module_name, tool_file)
            if spec is None or spec.loader is None:
                continue
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, "__is_tool__") and getattr(attr, "__is_tool__"):
                    self.__tools.append(attr)
                    info(f"Registered tool: {attr.__name__} - {getattr(attr, '__tool_description__', 'No description')}")
     
    def describe_tools(self) -> str:
        """
        返回一个字符串, 描述所有注册的工具函数及其功能
        """
        descriptions: list[tuple[str, int]] = []
        for tool in self.__tools:
            desc = getattr(tool, "__tool_description__", "No description")
            sort_value = getattr(tool, "__tool_sort__", None) or 0
            descriptions.append((f"{tool.__name__}: {desc}", sort_value))
        # 根据sort属性排序, 没有sort属性的工具默认排序为0
        descriptions.sort(key=lambda x: x[1])
        return f"<tools>\n{"".join([desc[0] + '\n' for desc in descriptions])}</tools>"

    def call_tool(self, name: str, **kwargs: Any) -> Any:
        """
        根据工具名称调用对应的工具函数, 并传入参数
        """
        for tool in self.__tools:
            if tool.__name__ == name:
                try:
                    debug(f"Calling tool '{name}' with arguments: {kwargs}")
                    result = tool(**kwargs)
                    debug(f"Tool '{name}' executed successfully with result: {result}")
                    return result
                except Exception as e:
                    error(f"Error calling tool '{name}': {str(e)}")
                    return f"Error: {str(e)}"
        error(f"Error: Tool '{name}' not found")
        raise ValueError(f"Error: Tool '{name}' not found")


# 解开下面的注释, 测试工具注册和调用功能
@decorator.tool("这是一个测试工具函数")
def test_tool(param: str):
    info(param)
    return f"Received: {param}"

if __name__ == "__main__":
    tools = Tools()
    info(tools.describe_tools())
    info(tools.call_tool("test_tool", param="Hello, World!"))