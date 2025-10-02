"""
工具函数模块
"""
import os
import hashlib
from pathlib import Path
from typing import List, Tuple

def parse_page_range(page_range_str: str, total_pages: int) -> List[int]:
    """
    解析页码范围字符串
    
    Args:
        page_range_str: 页码范围字符串,如 "1-5,7,10-12"
        total_pages: PDF总页数
        
    Returns:
        页码列表
    """
    pages = set()
    
    if not page_range_str:
        return list(range(1, total_pages + 1))
    
    parts = page_range_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        if '-' in part:
            # 范围,如 "1-5"
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            
            if start < 1 or end > total_pages:
                raise ValueError(f"页码范围 {start}-{end} 超出范围 (1-{total_pages})")
            
            pages.update(range(start, end + 1))
        else:
            # 单独页码
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"页码 {page} 超出范围 (1-{total_pages})")
            pages.add(page)
    
    return sorted(list(pages))


def get_file_hash(file_path: str) -> str:
    """
    获取文件的MD5哈希值
    
    Args:
        file_path: 文件路径
        
    Returns:
        MD5哈希值
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def ensure_dir(dir_path: str) -> Path:
    """
    确保目录存在,不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    验证PDF文件是否有效
    
    Args:
        file_path: PDF文件路径
        
    Returns:
        (是否有效, 错误消息)
    """
    path = Path(file_path)
    
    if not path.exists():
        return False, f"文件不存在: {file_path}"
    
    if not path.is_file():
        return False, f"不是文件: {file_path}"
    
    if path.suffix.lower() != '.pdf':
        return False, f"不是PDF文件: {file_path}"
    
    if path.stat().st_size == 0:
        return False, f"文件为空: {file_path}"
    
    return True, ""


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def estimate_cost(num_pages: int, provider: str = 'openai') -> str:
    """
    估算API调用成本
    
    Args:
        num_pages: 页数
        provider: LLM提供商
        
    Returns:
        成本估算字符串
    """
    # 粗略估算(实际成本会有差异)
    cost_per_page = {
        'openai': 0.03,  # GPT-4 Vision约$0.03/图
        'claude': 0.025,  # Claude 3约$0.025/图
        'gemini': 0.002,  # Gemini Pro Vision约$0.002/图
    }
    
    rate = cost_per_page.get(provider, 0.02)
    estimated_cost = num_pages * rate
    
    return f"约 ${estimated_cost:.2f} USD"
