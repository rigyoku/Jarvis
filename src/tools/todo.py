from pathlib import Path
from enum import Enum
from typing import List

import sys
sys.path.append(str(Path(__file__).parent.parent))

import decorator
from logger import info, critical

class Status(Enum):
    """任务状态枚举"""
    TODO = "todo"
    DOING = "doing"
    DONE = "done"

class Item:
    """待办任务项"""
    def __init__(self, id: int, context: str, status: Status = Status.TODO):
        self.id = id
        self.context = context
        self.status = status
    
    def __repr__(self):
        return f"Item(id={self.id}, context='{self.context}', status={self.status.value})"


__todo: List[Item] = []

def clean_todo():
    """清空待办列表"""
    global __todo
    __todo = []

@decorator.tool("列出所有待办项目")
def list_todo() -> str:
    """
    列出所有待办项目
    Returns:
        待办项目列表的字符串表示
    """
    return str(__todo)

@decorator.tool("""新增/修改待办项目内容""")
def update_todo(id: int, context: str, status: Status) -> str:
    """
    新增或修改待办项目内容
    Args:
        id: 项目ID
        context: 项目内容
        status: 项目状态
    Returns:
        更新后的待办列表内容
    """
    global __todo
    if status == Status.DOING:
        for item in __todo:
            if item.status == Status.DOING and item.id != id:
                return "待办列表中已经有一个项目处于doing状态!!"
    for item in __todo:
        if item.id == id:
            item.context = context
            item.status = status
            break
    else:
        if len(__todo) >= 10:
            return "待办列表数量已达上限10个!!"
        __todo.append(Item(id, context, status))
    critical(f"更新任务 {id} 状态为 {status.value} ==> {context}")
    return str(__todo)

if __name__ == "__main__":
    # 测试待办列表功能
    __todo.append(Item(3, "完成项目C"))
    clean_todo()
    __todo.append(Item(1, "完成项目A"))
    __todo.append(Item(2, "完成项目B"))
    info("初始待办列表: " + str(list_todo()))
    update_todo(1, "完成项目A - 已更新", Status.DOING)
    info("更新后待办列表: " + str(list_todo()))