import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from jinja2 import Environment, Template
from pathlib import Path

from app.schemas import (
    PromptTemplate, 
    CreatePromptTemplateRequest, 
    UpdatePromptTemplateRequest,
    PromptTemplateResponse,
    TemplateSearchRequest,
    TemplateListResponse
)
from app.utils import get_allowed_node_types, get_allowed_relations


class EnhancedPromptManager:
    def __init__(self, storage_file: str = "prompt_templates.json"):
        """
        增强的提示词管理器
        :param storage_file: 模板存储文件路径
        """
        self.storage_file = storage_file
        self.templates: Dict[str, PromptTemplate] = {}
        self.default_templates: Dict[str, str] = {}  # language -> template_id
        self.load_templates()
        
        # 初始化默认模板
        self._init_default_templates()

    def _init_default_templates(self):
        """初始化默认模板"""
        if not self.templates:
            # 创建默认的中文模板
            default_zh_template = PromptTemplate(
                id=str(uuid.uuid4()),
                name="默认中文模板",
                description="系统默认的中文提示词模板",
                language="zh",
                content=self._get_default_zh_content(),
                version="1.0.0",
                tags=["默认", "中文"],
                metadata={"is_default": True}
            )
            self.templates[default_zh_template.id] = default_zh_template
            self.default_templates["zh"] = default_zh_template.id
            
            # 创建默认的英文模板
            default_en_template = PromptTemplate(
                id=str(uuid.uuid4()),
                name="默认英文模板",
                description="系统默认的英文提示词模板",
                language="en",
                content=self._get_default_en_content(),
                version="1.0.0",
                tags=["默认", "英文"],
                metadata={"is_default": True}
            )
            self.templates[default_en_template.id] = default_en_template
            self.default_templates["en"] = default_en_template.id
            
            self.save_templates()

    def _get_default_zh_content(self) -> str:
        """获取默认中文模板内容"""
        return """# Knowledge Graph Extraction Prompt 

## 1. Overview
你是一个顶级信息抽取模型，专门从非结构化文本中提取结构化信息，用于构建知识图谱。
- **目标**：识别文本中的实体（节点）和它们之间的关系。
- **输出格式**：JSON 格式，包含 `nodes` 和 `relationships`。

## 2. 输出结构
{
  "nodes": [
    {
      "id": "实体唯一ID，如 disease_001",
      "name": "实体名称，如 高血压",
      "type": "实体类型，如 疾病、药物、人物、组织",
      "aliases": ["别名1", "别名2"],
      "definition": "实体简要定义（从文本中提取）",
      "attributes": {
        "属性名1": ["值1", "值2"],
        "属性名2": ["值1", "值2"]
      }
    }
  ],
  "relationships": [
    {
      "source": "源实体ID",
      "target": "目标实体ID",
      "type": "关系类型，如 作用于、属于、创立者等"
    }
  ]
}

## 3. Allowed Triplets (三元组限定)
- 只允许抽取下列三元组类型：
{% for triplet in allowed_triplets %}
- {{ triplet }}
{% endfor %}

## 4. 输入文本
{{ text }}

请根据上述要求提取知识图谱。"""

    def _get_default_en_content(self) -> str:
        """获取默认英文模板内容"""
        return """# Knowledge Graph Extraction Prompt

## 1. Overview
You are a top-tier information extraction model, specialized in extracting structured information from unstructured text for building knowledge graphs.
- **Goal**: Identify entities (nodes) and their relationships in the text.
- **Output Format**: JSON format containing `nodes` and `relationships`.

## 2. Output Structure
{
  "nodes": [
    {
      "id": "unique entity ID, e.g., disease_001",
      "name": "entity name, e.g., hypertension",
      "type": "entity type, e.g., disease, drug, person, organization",
      "aliases": ["alias1", "alias2"],
      "definition": "brief definition of the entity (extracted from text)",
      "attributes": {
        "attribute1": ["value1", "value2"],
        "attribute2": ["value1", "value2"]
      }
    }
  ],
  "relationships": [
    {
      "source": "source entity ID",
      "target": "target entity ID",
      "type": "relationship type, e.g., treats, belongs_to, founder_of"
    }
  ]
}

## 3. Allowed Triplets
- Only extract the following triplet types:
{% for triplet in allowed_triplets %}
- {{ triplet }}
{% endfor %}

## 4. Input Text
{{ text }}

Please extract the knowledge graph according to the above requirements."""

    def load_templates(self):
        """从文件加载模板"""
        if not os.path.exists(self.storage_file):
            self.templates = {}
            self.default_templates = {}
            return
        with open(self.storage_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.templates = {tid: PromptTemplate(**tpl) for tid, tpl in data.get("templates", {}).items()}
            # 自动识别默认模板
            self.default_templates = {}
            for tid, tpl in self.templates.items():
                if tpl.metadata.get("is_default"):
                    self.default_templates[tpl.language] = tid

    def save_templates(self):
        """保存模板到文件"""
        data = {"templates": {tid: tpl.dict() for tid, tpl in self.templates.items()}}
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_template(self, request: CreatePromptTemplateRequest) -> PromptTemplateResponse:
        """创建新模板"""
        template_id = str(uuid.uuid4())
        template = PromptTemplate(
            id=template_id,
            name=request.name,
            description=request.description,
            language=request.language,
            content=request.content,
            version="1.0.0",
            tags=request.tags,
            metadata=request.metadata
        )
        
        self.templates[template_id] = template
        
        self.save_templates()
        return PromptTemplateResponse(**template.dict())

    def update_template(self, template_id: str, request: UpdatePromptTemplateRequest) -> PromptTemplateResponse:
        """更新模板"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template = self.templates[template_id]
        if request.name is not None:
            template.name = request.name
        if request.description is not None:
            template.description = request.description
        if request.content is not None:
            template.content = request.content
        if request.tags is not None:
            template.tags = request.tags
        if request.metadata is not None:
            template.metadata = request.metadata
        template.updated_at = datetime.now()
        self.save_templates()
        return PromptTemplateResponse(**template.dict())

    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if template_id not in self.templates:
            return False
        
        del self.templates[template_id]
        self.save_templates()
        return True

    def get_template(self, template_id: str) -> Optional[PromptTemplateResponse]:
        """获取模板详情"""
        if template_id not in self.templates:
            return None
        return PromptTemplateResponse(**self.templates[template_id].dict())

    def list_templates(self, request: TemplateSearchRequest) -> TemplateListResponse:
        """列出模板"""
        templates = list(self.templates.values())
        
        # 应用过滤条件
        if request.language:
            templates = [t for t in templates if t.language == request.language]
        
        if request.tags:
            templates = [t for t in templates if any(tag in t.tags for tag in request.tags)]
        

        
        if request.keyword:
            keyword = request.keyword.lower()
            templates = [t for t in templates if 
                        keyword in t.name.lower() or 
                        keyword in t.description.lower()]
        
        # 分页
        total = len(templates)
        start = (request.page - 1) * request.page_size
        end = start + request.page_size
        templates = templates[start:end]
        
        return TemplateListResponse(
            templates=[PromptTemplateResponse(**t.dict()) for t in templates],
            total=total,
            page=request.page,
            page_size=request.page_size
        )

    def get_default_template(self, language: str) -> Optional[PromptTemplate]:
        """获取指定语言的默认模板"""
        if language not in self.default_templates:
            return None
        
        template_id = self.default_templates[language]
        return self.templates.get(template_id)

    def render_prompt(self, language: str, text: str, schema_info, template_id: Optional[str] = None) -> str:
        """渲染提示词"""
        # 如果指定了模板ID，使用指定模板
        if template_id:
            if template_id not in self.templates:
                raise ValueError(f"模板不存在: {template_id}")
            template = self.templates[template_id]
        else:
            # 否则使用默认模板
            template = self.get_default_template(language)
            if not template:
                raise ValueError(f"未找到语言 '{language}' 的默认模板")
        
        # 创建Jinja2环境
        env = Environment()
        jinja_template = env.from_string(template.content)
        
        # 提取schema信息
        allowed_node_types = get_allowed_node_types(schema_info.triplet)
        allowed_relations = get_allowed_relations(schema_info.triplet)
        allowed_triplets = schema_info.triplet
        
        # 渲染模板
        return jinja_template.render(
            text=text,
            allowed_node_types=allowed_node_types,
            allowed_relations=allowed_relations,
            allowed_triplets=allowed_triplets
        )

    def duplicate_template(self, template_id: str, new_name: str) -> PromptTemplateResponse:
        """复制模板"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        original = self.templates[template_id]
        new_template = PromptTemplate(
            id=str(uuid.uuid4()),
            name=new_name,
            description=f"复制自: {original.name}",
            language=original.language,
            content=original.content,
            version="1.0.0",
            tags=original.tags + ["复制"],
            metadata=original.metadata
        )
        
        self.templates[new_template.id] = new_template
        self.save_templates()
        return PromptTemplateResponse(**new_template.dict())

    def get_template_statistics(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        stats = {
            "total_templates": len(self.templates),
            "languages": {},
            "default_templates": len(self.default_templates),
            "recent_created": 0,
            "recent_updated": 0
        }
        
        # 按语言统计
        for template in self.templates.values():
            lang = template.language
            if lang not in stats["languages"]:
                stats["languages"][lang] = {"total": 0, "default": 0}
            stats["languages"][lang]["total"] += 1
            if template.id in self.default_templates.values():
                stats["languages"][lang]["default"] += 1
        
        # 最近创建和更新的模板数量
        now = datetime.now()
        for template in self.templates.values():
            if (now - template.created_at).days <= 7:
                stats["recent_created"] += 1
            if (now - template.updated_at).days <= 7:
                stats["recent_updated"] += 1
        
        return stats 