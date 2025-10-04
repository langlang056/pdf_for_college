"""
配置管理模块
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # LLM API配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-vision-preview')
    
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
    
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-pro-vision')
    
    # 默认LLM提供商
    DEFAULT_LLM_PROVIDER = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
    
    # PDF处理配置
    PDF_DPI = int(os.getenv('PDF_DPI', '200'))
    
    # 并发配置
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))
    
    # 重试和超时配置
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))
    
    # 上下文配置
    ENABLE_CONTEXT_LINKING = os.getenv('ENABLE_CONTEXT_LINKING', 'true').lower() == 'true'
    MAX_CONTEXT_PAGES = int(os.getenv('MAX_CONTEXT_PAGES', '3'))  # 保留最近N页的摘要
    
    # 缓存配置
    ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    
    # 默认提示词模板
    DEFAULT_PROMPT_TEMPLATE = """请作为一名专业的教师,详细分析这一页课件的内容。

请包括以下内容:
1. **主题概述**: 这一页的主要主题是什么?
2. **核心概念**: 列出并解释页面上的关键概念、定义或术语
3. **公式和图表**: 如果有数学公式、图表或图示,请详细解释它们的含义
4. **重点难点**: 指出这一页中学生可能难以理解的部分
5. **知识点总结**: 用简洁的语言总结这一页的要点
6. **与前文联系**: 如果提供了前面页面的信息,请说明这一页如何承接或深化前面的内容

请用清晰、易懂的中文回答,就像在给学生讲解一样。"""

    # 输出配置
    DEFAULT_OUTPUT_DIR = 'output'
    IMAGE_DIR_NAME = 'images'
    CACHE_DIR_NAME = 'cache'
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if cls.DEFAULT_LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("未配置 OPENAI_API_KEY,请在 .env 文件中设置")
        elif cls.DEFAULT_LLM_PROVIDER == 'claude' and not cls.ANTHROPIC_API_KEY:
            raise ValueError("未配置 ANTHROPIC_API_KEY,请在 .env 文件中设置")
        elif cls.DEFAULT_LLM_PROVIDER == 'gemini' and not cls.GOOGLE_API_KEY:
            raise ValueError("未配置 GOOGLE_API_KEY,请在 .env 文件中设置")
