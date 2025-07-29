# 三元组知识图谱抽取API

本项目基于 FastAPI，结合大语言模型（LLM），实现了从非结构化文本中自动抽取结构化三元组知识图谱的能力。支持自定义 schema、灵活的提示词模板、多语言扩展，适用于信息抽取、知识管理、智能问答等场景。

## 目录结构

```
.
├── app/                # 核心后端代码
│   ├── main.py         # FastAPI 入口
│   ├── kg_extractor.py # LLM抽取器
│   ├── prompt.py       # 提示词模板管理
│   ├── schemas.py      # 数据结构定义
│   └── utils.py        # 辅助工具函数
├── templates/          # Jinja2 提示词模板（支持中英文）
├── requirements.txt    # Python依赖
├── .env.example        # 环境变量配置示例
└── README.md           # 项目说明
```

## 主要特性

- 🚀 **一键部署**：基于 FastAPI，轻量高效，易于本地或云端部署。
- 🤖 **大模型驱动**：支持 OpenAI/火山方舟等 LLM，自动抽取实体与关系。
- 🧩 **自定义 Schema**：支持自定义三元组类型，灵活适配不同领域。
- 📝 **模板可扩展**：Jinja2 提示词模板，支持多语言和多风格切换。
- 🔒 **接口标准**：输入输出均为标准 JSON，便于集成与二次开发。

## 安装与运行

1. **克隆项目**
   ```bash
   git clone https://github.com/baixie-g/LLM-relations-extraction.git
   cd LLM-relations-extraction
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   - 复制 `.env.example` 文件为 `.env`，填写你的 LLM API 地址和密钥等信息。
   - 主要变量：
     ```
     ARK_API_KEY=你的API密钥
     LLM_API_BASE_URL=大模型API地址
     MODEL_NAME=模型名称（可选）
     ```

4. **启动服务**
   ```bash
   uvicorn app.main:app --reload
   ```
   默认监听 `http://127.0.0.1:8000`

## API 使用说明

### 1. 知识图谱抽取接口

- **URL**：`POST /extract`
- **请求体**（JSON）：

  ```json
  {
    "text": "小明毕业于清华大学，目前在字节跳动工作。",
    "schema": {
      "schema": "人物关系",
      "triplet": [
        "人物-毕业院校->学校",
        "人物-工作单位->公司"
      ]
    }
  }
  ```

- **返回体**（JSON）：

  ```json
  {
    "nodes": [
      {
        "id": "person_001",
        "name": "小明",
        "type": "人物",
        "aliases": [],
        "definition": "小明毕业于清华大学，目前在字节跳动工作。",
        "attributes": {
          "毕业院校": ["清华大学"],
          "工作单位": ["字节跳动"]
        }
      },
      {
        "id": "school_001",
        "name": "清华大学",
        "type": "学校",
        "aliases": [],
        "definition": "",
        "attributes": {}
      },
      {
        "id": "company_001",
        "name": "字节跳动",
        "type": "公司",
        "aliases": [],
        "definition": "",
        "attributes": {}
      }
    ],
    "relationships": [
      {
        "source": "person_001",
        "target": "school_001",
        "type": "毕业院校"
      },
      {
        "source": "person_001",
        "target": "company_001",
        "type": "工作单位"
      }
    ]
  }
  ```

### 2. Schema 说明

- `schema`：本次抽取的主题（如"人物关系"）。
- `triplet`：允许抽取的三元组类型，格式为 `实体-关系->目标`，如 `"人物-毕业院校->学校"`。

### 3. 节点与关系字段

- `nodes`：实体节点列表，包含 id、name、type、aliases、definition、attributes 等字段。
- `relationships`：实体间的关系，包含 source、target、type。

## 提示词模板自定义

- 模板文件位于 `templates/` 目录，支持中英文（如 `zh_prompt.j2`、`en_prompt.j2`）。
- 可根据实际需求修改模板内容，支持 few-shot 示例、输出格式、节点/关系规则等。

## 依赖环境

- Python 3.8+
- FastAPI
- Uvicorn
- OpenAI
- Pydantic
- Jinja2
- python-dotenv
- httpx[socks]

## 常见问题

- **API Key/模型地址配置错误**：请检查 `.env` 文件内容。
- **抽取结果为空或异常**：请确认 schema 合理、LLM 服务可用，或查看日志排查。

## 贡献与反馈

欢迎提交 issue 或 PR，完善功能与文档！

---

如需进一步补充（如详细的开发文档、二次开发说明、Docker 部署等），请告知你的具体需求！