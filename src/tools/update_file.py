import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import decorator

# 工作目录根路径
WORKSPACE_ROOT = Path(__file__).parent.parent.parent.resolve()

def _is_path_safe(file_path: str) -> tuple[bool, str, Path | None]:
    """检查文件路径是否安全，防止路径穿越
    
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

@decorator.tool("局部更新文件内容的工具函数. 接收参数 file_path (字符串, 要更新的文件路径), old_content (字符串, 要替换的旧内容) 和 new_content (字符串, 替换后的新内容). 返回值是一个字符串, 包含成功信息或者错误信息.")
def update_file(file_path: str, old_content: str, new_content: str) -> str:
    """局部更新文件内容（带安全检查）"""
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
        
        return f"Success: 文件更新成功，共替换 {count} 处内容 {resolved_path}"
    except UnicodeDecodeError:
        return f"Error: 文件不是文本文件，无法进行文本替换"
    except Exception as e:
        return f"Error: 更新文件失败 - {str(e)}"
