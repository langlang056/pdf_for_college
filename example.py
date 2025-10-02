"""
快速开始示例脚本
"""
from pathlib import Path
from config import Config
from pdf_processor import PDFProcessor
from llm_handler import create_llm_handler
from output_generator import OutputGenerator

def quick_start_example():
    """快速开始示例 - 处理单个PDF文件"""
    
    # 配置
    pdf_file = "your_lecture.pdf"  # 替换为你的PDF文件路径
    output_dir = "output"
    
    print("🚀 PDF课件讲解系统 - 快速开始")
    print("="*60)
    
    # 验证配置
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请先配置 .env 文件中的API密钥")
        return
    
    # 检查PDF文件
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        print("请将 'your_lecture.pdf' 替换为实际的PDF文件路径")
        return
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    image_dir = Path(output_dir) / "images"
    image_dir.mkdir(exist_ok=True)
    
    # 处理PDF
    print(f"\n📄 正在处理: {pdf_file}")
    
    with PDFProcessor(pdf_file) as processor:
        total_pages = processor.get_page_count()
        print(f"总页数: {total_pages}")
        
        # 只处理前3页作为示例
        pages_to_process = min(3, total_pages)
        print(f"示例: 处理前 {pages_to_process} 页")
        
        # 提取图像
        print("\n🖼️  提取页面图像...")
        image_paths = []
        for page_num in range(1, pages_to_process + 1):
            image = processor.extract_page_as_image(page_num)
            image_path = image_dir / f"page_{page_num:04d}.png"
            image.save(image_path, 'PNG')
            image_paths.append((page_num, str(image_path)))
            print(f"  ✓ 第 {page_num} 页")
        
        # 创建LLM处理器
        print(f"\n🤖 使用 {Config.DEFAULT_LLM_PROVIDER} 分析...")
        llm_handler = create_llm_handler(
            Config.DEFAULT_LLM_PROVIDER,
            Config,
            Config.DEFAULT_PROMPT_TEMPLATE
        )
        
        # 分析页面
        analyses = []
        for page_num, image_path in image_paths:
            print(f"  分析第 {page_num} 页...")
            analysis = llm_handler.analyze_image(image_path, page_num)
            analyses.append((page_num, image_path, analysis))
        
        # 生成输出
        print("\n📝 生成文档...")
        generator = OutputGenerator(output_dir, Path(pdf_file).name)
        
        md_file = generator.generate_markdown(analyses)
        html_file = generator.generate_html(analyses)
        
        print(f"\n✅ 完成!")
        print(f"  - Markdown: {md_file}")
        print(f"  - HTML: {html_file}")


def analyze_single_page(pdf_file: str, page_num: int):
    """分析单个页面的示例"""
    
    print(f"📄 分析单页: {pdf_file} 第 {page_num} 页")
    
    with PDFProcessor(pdf_file) as processor:
        if page_num > processor.get_page_count():
            print(f"❌ 页码超出范围")
            return
        
        # 提取图像
        image = processor.extract_page_as_image(page_num)
        temp_image_path = f"temp_page_{page_num}.png"
        image.save(temp_image_path)
        
        # 分析
        llm_handler = create_llm_handler(
            Config.DEFAULT_LLM_PROVIDER,
            Config,
            Config.DEFAULT_PROMPT_TEMPLATE
        )
        
        analysis = llm_handler.analyze_image(temp_image_path, page_num)
        
        print("\n" + "="*60)
        print(f"第 {page_num} 页讲解:")
        print("="*60)
        print(analysis)
        
        # 清理临时文件
        Path(temp_image_path).unlink()


if __name__ == '__main__':
    # 运行快速开始示例
    quick_start_example()
    
    # 或者分析单个页面
    # analyze_single_page("your_lecture.pdf", 1)
