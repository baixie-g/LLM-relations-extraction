from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from typing_extensions import Literal
from datetime import datetime

class SchemaItem(BaseModel):
    schema_name: str = Field(..., alias="schema", description="Schema name such as 'crime' or 'flights'")
    triplet: List[str] = Field(..., description="List of allowed triplets in the format 'Entity-Relation->Target'")

class ExtractionRequest(BaseModel):
    text: str = Field(..., description="The input text to extract knowledge graph from")
    schema_info: SchemaItem = Field(..., alias="schema", description="Schema information containing allowed entities and relations")
    language: str = Field("zh", description="Language code for template selection, default is 'zh'")
    template_id: Optional[str] = Field(None, description="Optional template ID to use, if not provided will use default template")

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node, formatted as type_number")
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type of the entity, e.g., Person, Organization")
    aliases: List[str] = Field(default_factory=list, description="List of alternative names or aliases")
    definition: str = Field("", description="A brief definition or description of the entity")
    attributes: Dict[str, List[Any]] = Field(default_factory=dict, description="Attributes of the entity, key-value pairs where values are arrays")

class Relationship(BaseModel):
    source: str = Field(..., description="Source entity ID")
    target: str = Field(..., description="Target entity ID")
    type: str = Field(..., description="Type of the relationship")

class ExtractionResponse(BaseModel):
    nodes: List[Node] = Field(..., description="List of extracted nodes")
    relationships: List[Relationship] = Field(..., description="List of extracted relationships")

# 新增的提示词管理相关模型
class PromptTemplate(BaseModel):
    id: str = Field(..., description="模板唯一标识符")
    name: str = Field(..., description="模板名称")
    description: str = Field("", description="模板描述")
    language: str = Field(..., description="语言代码，如 'zh' 或 'en'")
    content: str = Field(..., description="模板内容")
    version: str = Field("1.0.0", description="版本号")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class CreatePromptTemplateRequest(BaseModel):
    name: str = Field(..., description="模板名称")
    description: str = Field("", description="模板描述")
    language: str = Field(..., description="语言代码")
    content: str = Field(..., description="模板内容")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class UpdatePromptTemplateRequest(BaseModel):
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    content: Optional[str] = Field(None, description="模板内容")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    language: str
    content: str
    version: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    metadata: Dict[str, Any]

class PromptEvaluationRequest(BaseModel):
    test_texts: List[str] = Field(..., description="测试文本列表")
    schema_info: SchemaItem = Field(..., description="Schema信息")
    evaluation_metrics: List[str] = Field(default=["completeness", "accuracy"], description="评估指标")

class PromptEvaluationResponse(BaseModel):
    template_id: str
    template_name: str
    evaluation_results: Dict[str, float]
    detailed_results: List[Dict[str, Any]]
    summary: str

class TemplateListResponse(BaseModel):
    templates: List[PromptTemplateResponse]
    total: int
    page: int
    page_size: int

class TemplateSearchRequest(BaseModel):
    language: Optional[str] = Field(None, description="语言过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")