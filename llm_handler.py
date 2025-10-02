"""
LLM处理模块 - 负责与各种LLM API交互
"""
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any
import openai
from anthropic import Anthropic
import google.generativeai as genai
from PIL import Image

class LLMHandler:
    """LLM处理器基类"""
    
    def __init__(self, provider: str, api_key: str, model: str, prompt_template: str):
        """
        初始化LLM处理器
        
        Args:
            provider: LLM提供商 (openai, claude, gemini)
            api_key: API密钥
            model: 模型名称
            prompt_template: 提示词模板
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.prompt_template = prompt_template
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "") -> str:
        """
        分析图像并返回讲解内容
        
        Args:
            image_path: 图像文件路径
            page_num: 页码
            additional_context: 额外的上下文信息
            
        Returns:
            LLM生成的讲解内容
        """
        raise NotImplementedError("子类必须实现此方法")
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """将图像编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class OpenAIHandler(LLMHandler):
    """OpenAI处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str):
        super().__init__("openai", api_key, model, prompt_template)
        self.client = openai.OpenAI(api_key=api_key)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "") -> str:
        """使用OpenAI Vision API分析图像"""
        
        # 编码图像
        base64_image = self.encode_image_to_base64(image_path)
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        if additional_context:
            prompt += f"\n\n额外上下文:\n{additional_context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ 分析第 {page_num} 页时出错: {str(e)}"


class ClaudeHandler(LLMHandler):
    """Anthropic Claude处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str):
        super().__init__("claude", api_key, model, prompt_template)
        self.client = Anthropic(api_key=api_key)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "") -> str:
        """使用Claude Vision API分析图像"""
        
        # 读取并编码图像
        base64_image = self.encode_image_to_base64(image_path)
        
        # 获取图像类型
        image_type = Path(image_path).suffix[1:]  # 去掉点号
        if image_type == 'jpg':
            image_type = 'jpeg'
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        if additional_context:
            prompt += f"\n\n额外上下文:\n{additional_context}"
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_type}",
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ 分析第 {page_num} 页时出错: {str(e)}"


class GeminiHandler(LLMHandler):
    """Google Gemini处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str):
        super().__init__("gemini", api_key, model, prompt_template)
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "") -> str:
        """使用Gemini Vision API分析图像"""
        
        # 加载图像
        img = Image.open(image_path)
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        if additional_context:
            prompt += f"\n\n额外上下文:\n{additional_context}"
        
        try:
            response = self.model_instance.generate_content([prompt, img])
            return response.text
            
        except Exception as e:
            return f"❌ 分析第 {page_num} 页时出错: {str(e)}"


def create_llm_handler(provider: str, config: Any, prompt_template: str) -> LLMHandler:
    """
    工厂函数:创建LLM处理器
    
    Args:
        provider: LLM提供商
        config: 配置对象
        prompt_template: 提示词模板
        
    Returns:
        LLMHandler实例
    """
    if provider == 'openai':
        return OpenAIHandler(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            prompt_template=prompt_template
        )
    elif provider == 'claude':
        return ClaudeHandler(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.ANTHROPIC_MODEL,
            prompt_template=prompt_template
        )
    elif provider == 'gemini':
        return GeminiHandler(
            api_key=config.GOOGLE_API_KEY,
            model=config.GOOGLE_MODEL,
            prompt_template=prompt_template
        )
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
