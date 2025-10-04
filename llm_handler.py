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
    
    def __init__(self, provider: str, api_key: str, model: str, prompt_template: str, 
                 max_retries: int = 3, timeout: int = 60):
        """
        初始化LLM处理器
        
        Args:
            provider: LLM提供商 (openai, claude, gemini)
            api_key: API密钥
            model: 模型名称
            prompt_template: 提示词模板
            max_retries: 最大重试次数
            timeout: 超时时间(秒)
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.prompt_template = prompt_template
        self.max_retries = max_retries
        self.timeout = timeout
        self.previous_summaries = []  # 存储前面页面的摘要
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "", 
                     previous_context: str = "") -> str:
        """
        分析图像并返回讲解内容
        
        Args:
            image_path: 图像文件路径
            page_num: 页码
            additional_context: 额外的上下文信息
            previous_context: 前面页面的上下文摘要
            
        Returns:
            LLM生成的讲解内容
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def extract_summary(self, analysis_text: str, page_num: int) -> str:
        """
        从分析结果中提取关键摘要
        
        Args:
            analysis_text: 完整的分析文本
            page_num: 页码
            
        Returns:
            摘要文本
        """
        # 简单提取前200个字符作为摘要,或者可以调用LLM生成摘要
        lines = analysis_text.split('\n')
        summary_lines = []
        char_count = 0
        
        for line in lines:
            if char_count > 200:
                break
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
                char_count += len(line)
        
        summary = ' '.join(summary_lines)[:200]
        return f"[第{page_num}页摘要] {summary}"
    
    def add_to_context(self, summary: str, max_context_pages: int = 3):
        """
        添加摘要到上下文历史
        
        Args:
            summary: 页面摘要
            max_context_pages: 最大保留的上下文页数
        """
        self.previous_summaries.append(summary)
        # 只保留最近N页的摘要
        if len(self.previous_summaries) > max_context_pages:
            self.previous_summaries.pop(0)
    
    def get_context_string(self) -> str:
        """获取上下文字符串"""
        if not self.previous_summaries:
            return ""
        
        context = "\n".join(self.previous_summaries)
        return f"\n\n📚 前面页面的内容概要:\n{context}\n"
    
    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """将图像编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class OpenAIHandler(LLMHandler):
    """OpenAI处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str, 
                 max_retries: int = 3, timeout: int = 60):
        super().__init__("openai", api_key, model, prompt_template, max_retries, timeout)
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "",
                     previous_context: str = "") -> str:
        """使用OpenAI Vision API分析图像,支持重试"""
        
        # 编码图像
        base64_image = self.encode_image_to_base64(image_path)
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        
        # 添加前面页面的上下文
        if previous_context:
            prompt += previous_context
        
        if additional_context:
            prompt += f"\n\n📄 当前页面提取的文本:\n{additional_context}"
        
        # 重试机制
        for attempt in range(self.max_retries):
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
                error_msg = str(e)
                if attempt < self.max_retries - 1:
                    # 如果是超时或速率限制错误,等待后重试
                    if "timeout" in error_msg.lower() or "504" in error_msg or "429" in error_msg:
                        wait_time = (attempt + 1) * 5  # 递增等待时间
                        print(f"  ⚠️ 第{page_num}页请求失败,等待{wait_time}秒后重试... (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                
                return f"❌ 分析第 {page_num} 页时出错 (尝试{attempt + 1}次): {error_msg}"
        
        return f"❌ 分析第 {page_num} 页失败: 已达到最大重试次数"


class ClaudeHandler(LLMHandler):
    """Anthropic Claude处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str,
                 max_retries: int = 3, timeout: int = 60):
        super().__init__("claude", api_key, model, prompt_template, max_retries, timeout)
        self.client = Anthropic(api_key=api_key, timeout=timeout)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "",
                     previous_context: str = "") -> str:
        """使用Claude Vision API分析图像,支持重试"""
        
        # 读取并编码图像
        base64_image = self.encode_image_to_base64(image_path)
        
        # 获取图像类型
        image_type = Path(image_path).suffix[1:]  # 去掉点号
        if image_type == 'jpg':
            image_type = 'jpeg'
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        
        # 添加前面页面的上下文
        if previous_context:
            prompt += previous_context
            
        if additional_context:
            prompt += f"\n\n📄 当前页面提取的文本:\n{additional_context}"
        
        # 重试机制
        for attempt in range(self.max_retries):
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
                error_msg = str(e)
                if attempt < self.max_retries - 1:
                    if "timeout" in error_msg.lower() or "504" in error_msg or "429" in error_msg:
                        wait_time = (attempt + 1) * 5
                        print(f"  ⚠️ 第{page_num}页请求失败,等待{wait_time}秒后重试... (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                
                return f"❌ 分析第 {page_num} 页时出错 (尝试{attempt + 1}次): {error_msg}"
        
        return f"❌ 分析第 {page_num} 页失败: 已达到最大重试次数"


class GeminiHandler(LLMHandler):
    """Google Gemini处理器"""
    
    def __init__(self, api_key: str, model: str, prompt_template: str,
                 max_retries: int = 3, timeout: int = 60):
        super().__init__("gemini", api_key, model, prompt_template, max_retries, timeout)
        genai.configure(api_key=api_key)
        self.model_instance = genai.GenerativeModel(model)
        
    def analyze_image(self, image_path: str, page_num: int, 
                     additional_context: str = "",
                     previous_context: str = "") -> str:
        """使用Gemini Vision API分析图像,支持重试"""
        
        # 加载图像
        img = Image.open(image_path)
        
        # 构建提示词
        prompt = f"【第 {page_num} 页】\n\n{self.prompt_template}"
        
        # 添加前面页面的上下文
        if previous_context:
            prompt += previous_context
            
        if additional_context:
            prompt += f"\n\n📄 当前页面提取的文本:\n{additional_context}"
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                response = self.model_instance.generate_content([prompt, img])
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                if attempt < self.max_retries - 1:
                    if "timeout" in error_msg.lower() or "504" in error_msg or "429" in error_msg:
                        wait_time = (attempt + 1) * 5
                        print(f"  ⚠️ 第{page_num}页请求失败,等待{wait_time}秒后重试... (尝试 {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                
                return f"❌ 分析第 {page_num} 页时出错 (尝试{attempt + 1}次): {error_msg}"
        
        return f"❌ 分析第 {page_num} 页失败: 已达到最大重试次数"


def create_llm_handler(provider: str, config: Any, prompt_template: str,
                      max_retries: int = 3, timeout: int = 60) -> LLMHandler:
    """
    工厂函数:创建LLM处理器
    
    Args:
        provider: LLM提供商
        config: 配置对象
        prompt_template: 提示词模板
        max_retries: 最大重试次数
        timeout: 超时时间(秒)
        
    Returns:
        LLMHandler实例
    """
    if provider == 'openai':
        return OpenAIHandler(
            api_key=config.OPENAI_API_KEY,
            model=config.OPENAI_MODEL,
            prompt_template=prompt_template,
            max_retries=max_retries,
            timeout=timeout
        )
    elif provider == 'claude':
        return ClaudeHandler(
            api_key=config.ANTHROPIC_API_KEY,
            model=config.ANTHROPIC_MODEL,
            prompt_template=prompt_template,
            max_retries=max_retries,
            timeout=timeout
        )
    elif provider == 'gemini':
        return GeminiHandler(
            api_key=config.GOOGLE_API_KEY,
            model=config.GOOGLE_MODEL,
            prompt_template=prompt_template,
            max_retries=max_retries,
            timeout=timeout
        )
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")
