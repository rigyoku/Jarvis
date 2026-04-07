import os
from langchain.tools import tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from logger import info

# 工作目录根路径
WORKSPACE_ROOT = os.getcwd()

def _is_path_safe(file_path: str) -> tuple[bool, str, Path | None]:
    """检查文件路径是否安全,防止路径穿越
    
    Returns:
        (is_safe, error_message, resolved_path)
    """
    try:
        # 转换为绝对路径
        path = Path(file_path).resolve()
        
        # 检查是否在工作目录内
        if not str(path).startswith(str(WORKSPACE_ROOT)):
            return False, f"路径穿越被拒绝: 文件必须在工作目录 {WORKSPACE_ROOT} 内", path
        
        return True, "", path
    except Exception as e:
        return False, f"路径解析错误: {str(e)}", None

@tool
def read_file(file_path: str) -> str:
    """
    读取文件内容
    Args:
        file_path: 要读取的文件路径
    Returns:
        文件内容或者错误信息
    """
    # 安全检查
    is_safe, error_msg, resolved_path = _is_path_safe(file_path)
    if not is_safe:
        return f"Error: {error_msg}"
    
    try:
        if not resolved_path:
            return f"Error: 无法解析文件路径"
        
        # 检查文件是否存在
        if not resolved_path.exists():
            return f"Error: 文件不存在 {resolved_path}"
        
        # 检查是否为文件
        if not resolved_path.is_file():
            return f"Error: 路径不是文件 {resolved_path}"
        
        # 读取文件内容
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Success: 文件内容读取成功\n{content}"
    except UnicodeDecodeError:
        if not resolved_path:
            return f"Error: 无法解析文件路径"
        # 尝试以二进制方式读取
        try:
            with open(resolved_path, 'rb') as f:
                content = f.read()
            return f"Success: 文件为二进制文件,大小 {len(content)} 字节"
        except Exception as e:
            return f"Error: 读取文件失败 - {str(e)}"
    except Exception as e:
        return f"Error: 读取文件失败 - {str(e)}"


@tool
def update_file(file_path: str, old_content: str, new_content: str) -> str:
    """
    局部更新文件内容
    Args:
        file_path: 要更新的文件路径
        old_content: 要替换的旧内容
        new_content: 替换后的新内容
    Returns:
        成功信息或者错误信息
    """
    # 安全检查
    is_safe, error_msg, resolved_path = _is_path_safe(file_path)
    if not is_safe:
        return f"Error: {error_msg}"
    
    try:
        if not resolved_path:
            return f"Error: 无法解析文件路径"
        
        # 检查文件是否存在
        if not resolved_path.exists():
            return f"Error: 文件不存在 {resolved_path}"
        
        # 检查是否为文件
        if not resolved_path.is_file():
            return f"Error: 路径不是文件 {resolved_path}"
        
        # 读取文件内容
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查旧内容是否存在
        if old_content not in content:
            return f"Error: 未找到要替换的内容"
        
        # 统计替换次数
        count = content.count(old_content)
        
        # 执行替换
        updated_content = content.replace(old_content, new_content)
        
        # 写回文件
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return f"Success: 文件更新成功,共替换 {count} 处内容 {resolved_path}"
    except UnicodeDecodeError:
        return f"Error: 文件不是文本文件,无法进行文本替换"
    except Exception as e:
        return f"Error: 更新文件失败 - {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    写入文件内容
    Args:
        file_path: 要写入的文件路径
        content: 要写入的内容
    Returns:
        成功信息或者错误信息
    """
    # 安全检查
    is_safe, error_msg, resolved_path = _is_path_safe(file_path)
    if not is_safe:
        return f"Error: {error_msg}"
    
    try:
        if not resolved_path:
            return f"Error: 无法解析文件路径"
        
        # 确保父目录存在
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Success: 文件写入成功 {resolved_path}"
    except Exception as e:
        return f"Error: 写入文件失败 - {str(e)}"

if __name__ == "__main__":
    # 测试文件工具函数
    test_file = "debug/test_file.txt"
    
    # 测试写入文件
    info(write_file.invoke({
        "file_path": test_file, 
        "content": "Hello World"
    }))
    
    # 测试读取文件
    info(read_file.invoke({
        "file_path": test_file
    }))
    
    # 测试更新文件
    info(update_file.invoke({
        "file_path": test_file,
        "old_content": "World",
        "new_content": "Jarvis"
    }))
    
    # 再次读取文件验证更新
    info(read_file.invoke({
        "file_path": test_file
    }))
    
    # 测试文件工具函数
    test_file = "/tmp/test_dir/test_file.txt"
    
    # 测试写入文件
    info(write_file.invoke({
        "file_path": test_file, 
        "content": "Hello World"
    }))
    
    # 测试读取文件
    info(read_file.invoke({
        "file_path": test_file
    }))
    
    # 测试更新文件
    info(update_file.invoke({
        "file_path": test_file,
        "old_content": "World",
        "new_content": "Jarvis"
    }))
    
    # 再次读取文件验证更新
    info(read_file.invoke({
        "file_path": test_file
    }))