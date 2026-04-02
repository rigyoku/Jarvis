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

@decorator.tool("写入文件内容的工具函数. 接收参数 file_path (字符串, 要写入的文件路径) 和 content (字符串, 要写入的内容). 返回值是一个字符串, 包含成功信息或者错误信息.")
def write_file(file_path: str, content: str) -> str:
    """写入文件内容（带安全检查）"""
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
