# 知识图谱抽取系统 - 动态提示词管理版

本项目基于 FastAPI，结合大语言模型（LLM），实现了从非结构化文本中自动抽取结构化三元组知识图谱的能力。支持自定义 schema、灵活的提示词模板、多语言扩展，适用于信息抽取、知识管理、智能问答等场景。

## 🚀 新功能特性

### 1. 动态提示词管理
- **模板创建**: 支持创建自定义的提示词模板
- **模板编辑**: 实时修改现有模板内容
- **模板激活**: 动态切换不同语言的激活模板
- **模板复制**: 快速复制现有模板进行修改
- **模板删除**: 安全删除不需要的模板

### 2. 提示词评估系统
- **多维度评估**: 完整性、准确性、一致性、相关性
- **批量测试**: 支持多个测试文本同时评估
- **详细报告**: 提供详细的评估结果和建议
- **性能对比**: 比较不同模板的效果

### 3. Web管理界面
- **直观界面**: 现代化的Web管理界面
- **实时操作**: 无需重启服务即可修改提示词
- **统计信息**: 模板使用情况和效果统计
- **搜索过滤**: 支持按语言、标签、关键词搜索

### 4. 版本控制
- **模板版本**: 每个模板都有版本号
- **激活状态**: 支持模板的激活/停用
- **元数据管理**: 支持标签和自定义元数据

## 📋 API接口

### 知识图谱抽取
```http
POST /extract
Content-Type: application/json

{
  "text": "输入文本",
  "schema": {
    "schema": "medical",
    "triplet": ["疾病-症状->症状", "药物-治疗->疾病"]
  }
}
```

### 提示词模板管理

#### 创建模板
```http
POST /prompts
Content-Type: application/json

{
  "name": "医疗领域模板",
  "description": "专门用于医疗领域的知识图谱抽取",
  "language": "zh",
  "content": "Jinja2模板内容...",
  "tags": ["医疗", "疾病", "药物"],
  "metadata": {"domain": "medical"}
}
```

#### 获取模板列表
```http
GET /prompts?language=zh&page=1&page_size=10
```

#### 获取模板详情
```http
GET /prompts/{template_id}
```

#### 更新模板
```http
PUT /prompts/{template_id}
Content-Type: application/json

{
  "name": "更新后的模板名称",
  "content": "更新后的模板内容"
}
```

#### 激活模板
```http
POST /prompts/{template_id}/activate
```

#### 复制模板
```http
POST /prompts/{template_id}/duplicate?new_name=新模板名称
```

#### 删除模板
```http
DELETE /prompts/{template_id}
```

### 模板评估

#### 评估模板效果
```http
POST /prompts/{template_id}/evaluate
Content-Type: application/json

{
  "test_texts": [
    "测试文本1",
    "测试文本2"
  ],
  "schema_info": {
    "schema": "medical",
    "triplet": ["疾病-症状->症状", "药物-治疗->疾病"]
  },
  "evaluation_metrics": ["completeness", "accuracy", "consistency"]
}
```

### 统计信息

#### 获取统计信息
```http
GET /prompts/statistics
```

#### 获取激活模板
```http
GET /prompts/active/{language}
```

## 🛠️ 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key
```

### 3. 运行服务
```bash
python -m app.main
```

### 4. 访问Web界面
打开浏览器访问：http://localhost:8000

## 📖 使用示例

### 1. 创建自定义模板

```python
import requests

# 创建新的提示词模板
template_data = {
    "name": "金融领域模板",
    "description": "专门用于金融领域的知识图谱抽取",
    "language": "zh",
    "content": """
# 金融知识图谱抽取

你是一个专业的金融信息抽取模型。

## 输出格式
{
  "nodes": [
    {
      "id": "entity_id",
      "name": "实体名称",
      "type": "实体类型",
      "aliases": ["别名"],
      "definition": "定义",
      "attributes": {"属性": ["值"]}
    }
  ],
  "relationships": [
    {
      "source": "源实体ID",
      "target": "目标实体ID",
      "type": "关系类型"
    }
  ]
}

## 输入文本
{{ text }}

## 允许的三元组
{% for triplet in allowed_triplets %}
- {{ triplet }}
{% endfor %}
""",
    "tags": ["金融", "投资", "股票"],
    "metadata": {"domain": "finance"}
}

response = requests.post("http://localhost:8000/prompts", json=template_data)
print(response.json())
```

### 2. 评估模板效果

```python
# 评估模板效果
evaluation_data = {
    "test_texts": [
        "阿里巴巴是一家中国电子商务公司，由马云创立于1999年。",
        "腾讯控股有限公司是一家中国互联网公司，主要业务包括社交网络、游戏等。"
    ],
    "schema_info": {
        "schema": "company",
        "triplet": ["公司-创始人->人物", "公司-业务->业务类型"]
    },
    "evaluation_metrics": ["completeness", "accuracy", "consistency"]
}

response = requests.post(
    "http://localhost:8000/prompts/{template_id}/evaluate", 
    json=evaluation_data
)
print(response.json())
```

## 🎯 评估指标说明

- **完整性**：提取内容覆盖文本主要信息，分数0-1
- **准确性**：提取内容正确，分数0-1
- **一致性**：输出格式规范，分数0-1
- **相关性**：实体与原文相关，分数0-1

## 🔧 配置说明

### 模板存储
- 模板数据存储在 `prompt_templates.json` 文件中
- 支持自动备份和恢复
- 支持导入/导出功能

### 评估配置
- 可自定义评估指标权重
- 支持批量评估和对比分析
- 提供详细的评估报告

## 📝 开发说明

### 项目结构
```
三元组/
├── app/
│   ├── main.py              # 主应用文件
│   ├── schemas.py           # 数据模型
│   ├── prompt_manager.py    # 提示词管理器
│   ├── prompt_evaluator.py  # 提示词评估器
│   ├── kg_extractor.py      # 知识图谱抽取器
│   └── utils.py             # 工具函数
├── templates/
│   ├── index.html           # Web管理界面
│   └── *.j2                 # 原始模板文件
├── requirements.txt         # 依赖列表
└── README.md               # 说明文档
```

### 扩展开发
1. **添加新的评估指标**: 在 `PromptEvaluator` 类中添加新的评估方法
2. **自定义模板引擎**: 修改 `EnhancedPromptManager` 类支持更多模板引擎
3. **数据库存储**: 将文件存储改为数据库存储以提高性能
4. **用户权限**: 添加用户认证和权限管理

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

MIT License