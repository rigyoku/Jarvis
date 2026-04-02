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

@decorator.tool("读取文件内容的工具函数. 接收参数 file_path, 是一个字符串, 表示要读取的文件路径. 返回值是一个字符串, 包含文件内容或者错误信息.")
def read_file(file_path: str) -> str:
    """读取文件内容（带安全检查）"""
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
            return f"Success: 文件为二进制文件，大小 {len(content)} 字节"
        except Exception as e:
            return f"Error: 读取文件失败 - {str(e)}"
    except Exception as e:
        return f"Error: 读取文件失败 - {str(e)}"
