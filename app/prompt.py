import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List

from app.schemas import SchemaItem
from app.utils import get_allowed_node_types, get_allowed_relations


class PromptManager:
    def __init__(self, template_dir: str = "templates"):
        """
        初始化提示词模板管理器
        :param template_dir: 模板文件夹路径
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def load_template(self, lang: str = "zh") -> str:
        """
        根据语言加载对应的提示词模板
        :param lang: 语言代码，如 "zh" 或 "en"
        :return: 模板名称
        """
        if lang not in ["zh", "en"]:
            raise ValueError(f"Unsupported language: {lang}")
        return f"{lang}_prompt.j2"

    def render_prompt(
        self,
        lang: str,
        text: str,
        schema: SchemaItem
    ) -> str:
        """
        渲染完整的提示词内容
        :param lang: 语言代码
        :param text: 输入文本
        :param schema: Schema 信息
        :return: 渲染后的提示词字符串
        """
        template_name = self.load_template(lang)
        template = self.env.get_template(template_name)

        # 提取 schema 中允许的节点和关系类型
        allowed_node_types = get_allowed_node_types(schema.triplet)
        allowed_relations = get_allowed_relations(schema.triplet)
        allowed_triplets = schema.triplet

        # 渲染模板
        rendered_prompt = template.render(
            text=text,
            allowed_node_types=allowed_node_types,
            allowed_relations=allowed_relations,
            allowed_triplets=allowed_triplets
        )

        return rendered_prompt