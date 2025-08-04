from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from app.schemas import (
    ExtractionRequest, 
    ExtractionResponse,
    CreatePromptTemplateRequest,
    UpdatePromptTemplateRequest,
    PromptTemplateResponse,
    TemplateListResponse,
    PromptEvaluationRequest,
    PromptEvaluationResponse,
    TemplateSearchRequest
)
from app.prompt_manager import EnhancedPromptManager
from app.prompt_evaluator import PromptEvaluator
from app.kg_extractor import LLMKGExtractor
import logging
import os

# 初始化FastAPI应用
app = FastAPI(
    title="知识图谱抽取API",
    description="支持动态提示词管理的知识图谱抽取服务",
    version="2.0.0"
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化组件
prompt_manager = EnhancedPromptManager()
kg_extractor = LLMKGExtractor()
prompt_evaluator = PromptEvaluator()

# 挂载静态文件
if os.path.exists("templates"):
    app.mount("/static", StaticFiles(directory="templates"), name="static")

# ==================== Web界面接口 ====================

@app.get("/")
async def read_root():
    """返回Web管理界面"""
    return FileResponse("templates/index.html")

# ==================== 知识图谱抽取接口 ====================

@app.post("/extract", response_model=ExtractionResponse)
async def extract_knowledge_graph(extraction_request: ExtractionRequest) -> ExtractionResponse:
    """
    提取知识图谱接口
    :param extraction_request: 包含文本和schema信息的请求体
    :return: 结构化的知识图谱数据
    """
    try:
        logger.info(f"Extraction schema_info: {extraction_request.schema_info}")
        logger.info(f"Template ID: {extraction_request.template_id}")
        
        # 使用增强的提示词管理器渲染提示词
        prompt = prompt_manager.render_prompt(
            language=extraction_request.language,
            text=extraction_request.text,
            schema_info=extraction_request.schema_info,
            template_id=extraction_request.template_id
        )
        
        # 调用LLM进行知识图谱抽取
        logger.info(f"Prompt: {prompt}")
        result = kg_extractor.extract(prompt)
        
        # 返回结果
        return ExtractionResponse(**result)
    
    except Exception as e:
        logger.error(f"Error during knowledge graph extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 提示词模板管理接口 ====================

@app.post("/prompts", response_model=PromptTemplateResponse)
async def create_prompt_template(request: CreatePromptTemplateRequest) -> PromptTemplateResponse:
    """
    创建新的提示词模板
    """
    try:
        return prompt_manager.create_template(request)
    except Exception as e:
        logger.error(f"Error creating prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prompts", response_model=TemplateListResponse)
async def list_prompt_templates(
    language: Optional[str] = Query(None, description="语言过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，用逗号分隔"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
) -> TemplateListResponse:
    """
    列出提示词模板
    """
    try:
        request = TemplateSearchRequest(
            language=language,
            tags=tags.split(",") if tags else None,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        return prompt_manager.list_templates(request)
    except Exception as e:
        logger.error(f"Error listing prompt templates: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 统计信息接口 ====================

@app.get("/prompts/statistics")
async def get_prompt_statistics():
    """
    获取提示词模板统计信息
    """
    try:
        return prompt_manager.get_template_statistics()
    except Exception as e:
        logger.error(f"Error getting prompt statistics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/prompts/{template_id}", response_model=PromptTemplateResponse)
async def get_prompt_template(template_id: str) -> PromptTemplateResponse:
    """
    获取提示词模板详情
    """
    try:
        template = prompt_manager.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/prompts/{template_id}", response_model=PromptTemplateResponse)
async def update_prompt_template(
    template_id: str, 
    request: UpdatePromptTemplateRequest
) -> PromptTemplateResponse:
    """
    更新提示词模板
    """
    try:
        return prompt_manager.update_template(template_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/prompts/{template_id}")
async def delete_prompt_template(template_id: str):
    """
    删除提示词模板
    """
    try:
        success = prompt_manager.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        return {"message": "模板删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/prompts/{template_id}/duplicate", response_model=PromptTemplateResponse)
async def duplicate_prompt_template(
    template_id: str, 
    new_name: str = Query(..., description="新模板名称")
) -> PromptTemplateResponse:
    """
    复制提示词模板
    """
    try:
        return prompt_manager.duplicate_template(template_id, new_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 提示词评估接口 ====================

@app.post("/prompts/{template_id}/evaluate", response_model=PromptEvaluationResponse)
async def evaluate_prompt_template(
    template_id: str,
    request: PromptEvaluationRequest
) -> PromptEvaluationResponse:
    """
    评估提示词模板效果
    """
    try:
        # 获取模板信息
        template = prompt_manager.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        # 执行评估
        return prompt_evaluator.evaluate_template(
            template_id=template_id,
            template_name=template.name,
            template_content=template.content,
            test_texts=request.test_texts,
            schema_info=request.schema_info,
            evaluation_metrics=request.evaluation_metrics
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating prompt template: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 健康检查接口 ====================

@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "prompt_manager": "running",
            "kg_extractor": "running",
            "prompt_evaluator": "running"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)