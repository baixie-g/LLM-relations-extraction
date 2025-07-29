from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.schemas import ExtractionRequest, ExtractionResponse
from app.prompt import PromptManager
from app.kg_extractor import LLMKGExtractor
import logging

# 初始化FastAPI应用
app = FastAPI()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化提示词管理器和LLM知识图谱抽取器
prompt_manager = PromptManager()
kg_extractor = LLMKGExtractor()

@app.post("/extract", response_model=ExtractionResponse)
async def extract_knowledge_graph(extraction_request: ExtractionRequest) -> ExtractionResponse:
    """
    提取知识图谱接口
    :param extraction_request: 包含文本和schema信息的请求体
    :return: 结构化的知识图谱数据
    """
    try:
        logger.info(f"Extraction schema_info: {extraction_request.schema_info}")
        # 根据语言选择模板并渲染提示词
        prompt = prompt_manager.render_prompt(
            lang="zh",
            text=extraction_request.text,
            schema=extraction_request.schema_info
        )
        
        # 调用LLM进行知识图谱抽取
        logger.info(f"Prompt: {prompt}")
        result = kg_extractor.extract(prompt)
        
        # 返回结果
        return ExtractionResponse(**result)
    
    except Exception as e:
        logger.error(f"Error during knowledge graph extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)