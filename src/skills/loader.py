import os
from typing import List
from langchain.tools import tool

import yaml
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from logger import info, debug, warning, error

WORKSPACE_ROOT = os.getcwd()
SKILL_DIR = "skills"


@dataclass
class SkillMeta:
    name: str
    description: str

@dataclass
class Skill(SkillMeta):
    content: str
    file_path: str
    
__skill_definitions: List[Skill] = []

def __load_skills_from_yaml() -> None:
    """
    读取当前文件夹下所有的.yml文件, 并解析其中的技能定义,返回一个技能定义列表
    元数据和内容用---分割
    """
    
    debug(f"Scanning for YAML files in {WORKSPACE_ROOT}/{SKILL_DIR}...")
    for yaml_file in Path(WORKSPACE_ROOT, SKILL_DIR).glob("*.yml"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            try:
                splited = f.read().split("---", 1)
                meta = splited[0]
                content = splited[1] if len(splited) > 1 else ""
                data: SkillMeta = yaml.safe_load(meta)
                if isinstance(data, dict) and "name" in data and "description" in data:
                    skill = Skill(
                        name=data.get("name", "Unnamed Skill"), # type: ignore
                        description=data.get("description", "No description"), # type: ignore
                        content=content,
                        file_path=str(yaml_file)
                    )
                    info(f"Loaded skill: {skill.name} - {skill.description} (from {skill.file_path})")
                    debug(f"Content:\n{skill.content}\n{'-'*40}")
                    __skill_definitions.append(skill)
                else:
                    warning(f"Warning: 文件 {yaml_file} 中缺少必要的字段 (name, description),已跳过")
            except yaml.YAMLError as e:
                error(f"Error parsing YAML file {yaml_file}: {e}")

def get_metadata() -> str:
    """
    获取技能的元数据列表,每个元素包含 name 和 description 字段
    Returns:
        技能元数据列表
    """
    if not __skill_definitions:
        __load_skills_from_yaml()
    return str([{"name": skill.name, "description": skill.description} for skill in __skill_definitions])

@tool
def get_skill_content(name: str) -> str | None:
    """
    根据技能名称获取技能内容
    Args:
        name: 技能名称
    Returns:
        技能内容字符串,如果未找到则返回 None
    """
    if not __skill_definitions:
        __load_skills_from_yaml()
    for skill in __skill_definitions:
        if skill.name == name:
            return skill.content
    warning(f"Warning: 未找到技能 {name}")
    return None


if __name__ == "__main__":
    __load_skills_from_yaml()
    info(f"Total skills loaded: {len(__skill_definitions)}")
    info(f"Metadata: {get_metadata()}")
    info(f"Content of first skill: {get_skill_content.invoke(__skill_definitions[0].name) if __skill_definitions else 'No skills loaded'}")