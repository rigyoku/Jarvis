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
    """看板任务项"""
    def __init__(self, id: int, context: str, status: Status = Status.TODO):
        self.id = id
        self.context = context
        self.status = status
    
    def __repr__(self):
        return f"Item(id={self.id}, context='{self.context}', status={self.status.value})"


__kanban: List[Item] = []

def clean_kanban():
    """清空看板"""
    global __kanban
    __kanban = []

@decorator.tool("列出看板所有项目", sort=-100)
def list_kanban() -> str:
    return str(__kanban)

@decorator.tool("""新增/修改看板项目内容, 接收参数id, context, status.
id是项目id int类型, context是新的项目内容 str类型, status是新的项目状态 Status类型(todo/doing/done).
返回更新后的项目列表.
看板最多只能有10个项目, 同时只能有一个doing状态的项目.""", sort=-99)
def update_kanban(id: int, context: str, status: Status) -> str:
    global __kanban
    if status == Status.DOING:
        for item in __kanban:
            if item.status == Status.DOING and item.id != id:
                return "看板中已经有一个项目处于doing状态!!"
    for item in __kanban:
        if item.id == id:
            item.context = context
            item.status = status
            break
    else:
        if len(__kanban) >= 10:
            return "看板项目数量已达上限10个!!"
        __kanban.append(Item(id, context, status))
    critical(f"更新任务 {id} 状态为 {status.value} ==> {context}")
    return str(__kanban)

if __name__ == "__main__":
    # 测试看板功能
    __kanban.append(Item(3, "完成项目C"))
    clean_kanban()
    __kanban.append(Item(1, "完成项目A"))
    __kanban.append(Item(2, "完成项目B"))
    info("初始看板: " + str(list_kanban()))
    update_kanban(1, "完成项目A - 已更新", Status.DOING)
    info("更新后看板: " + str(list_kanban()))