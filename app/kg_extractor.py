from openai import OpenAI
import os
import json
from typing import Dict, Any
from app.utils import setup_logger

# 设置日志
logger = setup_logger(__name__)

class LLMKGExtractor:
    def __init__(self):
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=os.getenv("LLM_API_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=os.environ.get("ARK_API_KEY"),
        )
        self.model = os.getenv("MODEL_NAME", "ep-20250716102319-wdqpt")

    def extract(self, prompt: str) -> Dict[str, Any]:
        """
        调用LLM进行知识图谱抽取
        :param prompt: 渲染后的提示词字符串
        :return: 解析后的JSON结果
        """
        try:
            logger.info(f"Sending request to LLM with prompt length {len(prompt)}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            content = (response.choices[0].message.content or "").strip()
            logger.info(f"Received response from LLM: {content[:100]}...")  # 只打印前100个字符作为示例
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error during LLM call: {str(e)}")
            raise ValueError("Failed to process the request through LLM.") from e


if __name__ == "__main__":
    # 示例测试
    extractor = LLMKGExtractor()
    test_prompt = "这是一个测试提示词。"
    try:
        result = extractor.extract(test_prompt)
        print(result)
    except ValueError as ve:
        print(ve)