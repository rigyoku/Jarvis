import threading
from typing import Callable, Any, TypeVar, Type

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from logger import info

# 定义泛型类型，用于保留原始类的类型信息
T = TypeVar("T")

def singleton(cls: Type[T]) -> Callable[..., T]:
    """
    装饰器，用于将一个类变成单例模式（线程安全）

    Args:
        cls: 需要变成单例的类

    Returns:
        包装后的函数，调用后始终返回同一个实例
    """
    _instance: T | None = None
    _lock: threading.Lock = threading.Lock()

    def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal _instance
        if _instance is None:
            with _lock:
                if _instance is None:
                    _instance = cls(*args, **kwargs)
        return _instance

    return wrapper

if __name__ == "__main__":
    @singleton
    class MyClass:
        def __init__(self, value: int) -> None:
            self.value = value
            info(f"MyClass instance created with value: {value}")

    obj1 = MyClass(10)
    obj2 = MyClass(20)
    info(obj1 is obj2)