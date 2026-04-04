import subprocess
import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator
from logger import info

# 危险命令黑名单
DANGEROUS_COMMANDS = [
    r'\brm\s+-rf\s+/',  # 删除根目录
    r'\brm\s+-rf\s+\*',  # 删除所有文件
    r'\b(sudo\s+)?dd\b',  # 磁盘操作
    r'\bmkfs\b',  # 格式化
    r'\bformat\b',  # 格式化
    r'\bshutdown\b',  # 关机
    r'\breboot\b',  # 重启
    r'\binit\s+[06]',  # 关机/重启
    r'\bfdisk\b',  # 磁盘分区
    r'\b:\(\)\s*\{',  # Fork bomb
    r'>\s*/dev/sd[a-z]',  # 直接写入磁盘
    r'\bchmod\s+-R\s+777',  # 危险权限修改
    r'\bwget.*\|\s*bash',  # 下载并执行
    r'\bcurl.*\|\s*bash',  # 下载并执行
    r'\biptables\s+-F',  # 清空防火墙规则
]

def _is_command_safe(command: str) -> tuple[bool, str]:
    """检查命令是否安全
    
    Returns:
        (is_safe, error_message)
    """
    command_lower = command.lower()
    
    # 检查危险命令模式
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"检测到危险命令模式: {pattern}"
    
    # 检查是否包含多个命令连接（可能用于绕过检查）
    if any(sep in command for sep in [';', '&&', '||']) and any(danger in command_lower for danger in ['rm', 'dd', 'format', 'mkfs']):
        return False, "检测到潜在的命令链接危险操作"
    
    return True, ""

@decorator.tool("执行系统命令的工具函数. 接收参数 command, 是一个字符串, 表示要执行的系统命令. 返回值是一个字符串, 包含命令的输出结果或者错误信息. 禁止执行危险的系统命令. 该工具为兜底工具, 尽可能使用其他工具来完成任务, 只有在确实需要执行系统命令时才使用该工具.", sort=100)
def exec(command: str) -> str:
    """执行一个系统命令（带安全检查）"""
    # 安全检查
    is_safe, error_msg = _is_command_safe(command)
    if not is_safe:
        return f"Error: 命令被安全策略拒绝 - {error_msg}"
    
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

if __name__ == "__main__":
    # 测试安全命令
    info(exec("echo Hello World"))
    # 测试危险命令
    info(exec("rm -rf /"))