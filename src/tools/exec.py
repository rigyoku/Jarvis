import subprocess

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator

@decorator.tool("执行系统命令的工具函数. 接收参数 command, 是一个字符串, 表示要执行的系统命令. 返回值是一个字符串, 包含命令的输出结果或者错误信息.")
def exec(command: str) -> str:
    """执行一个系统命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return f"Success: {result.stdout}" if result.returncode == 0 else f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"
    