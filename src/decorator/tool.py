from typing import Callable, TypeVar, ParamSpec
from functools import wraps

# 定义泛型类型，用于保留原始函数的类型信息
P = ParamSpec("P")
R = TypeVar("R")

def tool(description: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    装饰器，用于标记一个函数为工具函数，并提供描述信息

    Args:
        description: 工具函数的描述信息

    Returns:
        装饰后的函数，附带工具描述元数据
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)
        
        # 将描述信息存储在函数的属性中
        setattr(wrapper, "__tool_description__", description)
        setattr(wrapper, "__is_tool__", True)
        
        return wrapper
    
    return decorator

if __name__ == "__main__":
    @tool("执行系统命令的工具函数")
    def execute_command(command: str) -> str:
        """执行一个系统命令"""
        print(f"Executing: {command}")
        return f"Result of: {command}"
    
    # 测试装饰器
    result = execute_command("ls -la")
    print(result)
    print(f"Is tool: {getattr(execute_command, '__is_tool__', False)}")
    print(f"Description: {getattr(execute_command, '__tool_description__', 'No description')}")
