#!/usr/bin/env python3
"""
PDF课件自动讲解系统 - 主程序
"""
import sys
import argparse
from pathlib import Path
from tqdm import tqdm
import time

from config import Config
from pdf_processor import PDFProcessor
from llm_handler import create_llm_handler
from output_generator import OutputGenerator
from utils import (
    parse_page_range, validate_pdf_file, ensure_dir,
    format_file_size, estimate_cost
)


def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='PDF课件自动讲解系统 - 自动分析PDF课件并生成详细讲解'
    )
    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument('-o', '--output', default=Config.DEFAULT_OUTPUT_DIR,
                       help='输出目录 (默认: output)')
    parser.add_argument('--llm', default=Config.DEFAULT_LLM_PROVIDER,
                       choices=['openai', 'claude', 'gemini'],
                       help='LLM提供商 (默认: openai)')
    parser.add_argument('--prompt', default=Config.DEFAULT_PROMPT_TEMPLATE,
                       help='自定义提示词模板')
    parser.add_argument('--pages', default='',
                       help='页码范围,如 "1-5,7,10-12" (默认: 所有页)')
    parser.add_argument('--dpi', type=int, default=Config.PDF_DPI,
                       help='图像分辨率DPI (默认: 200)')
    parser.add_argument('--no-cache', action='store_true',
                       help='禁用缓存')
    parser.add_argument('--format', choices=['markdown', 'html', 'both'],
                       default='both', help='输出格式 (默认: both)')
    
    args = parser.parse_args()
    
    # 验证PDF文件
    is_valid, error_msg = validate_pdf_file(args.pdf_file)
    if not is_valid:
        print(f"❌ 错误: {error_msg}")
        sys.exit(1)
    
    pdf_path = Path(args.pdf_file)
    print(f"\n📚 PDF课件自动讲解系统")
    print(f"{'='*60}")
    print(f"📄 文件: {pdf_path.name}")
    print(f"📊 大小: {format_file_size(pdf_path.stat().st_size)}")
    print(f"🤖 LLM: {args.llm}")
    print(f"📁 输出: {args.output}")
    print(f"{'='*60}\n")
    
    # 验证配置
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n💡 提示: 请复制 .env.example 到 .env 并配置你的API密钥")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = ensure_dir(args.output)
    image_dir = ensure_dir(output_dir / Config.IMAGE_DIR_NAME)
    cache_dir = ensure_dir(output_dir / Config.CACHE_DIR_NAME)
    
    # 初始化组件
    output_generator = OutputGenerator(str(output_dir), pdf_path.name)
    
    # 检查缓存
    cached_analyses = None
    if Config.ENABLE_CACHE and not args.no_cache:
        print("🔍 检查缓存...")
        cached_analyses = output_generator.load_cache(str(cache_dir))
        if cached_analyses:
            print(f"✅ 找到缓存,共 {len(cached_analyses)} 页")
            use_cache = input("是否使用缓存? (y/n): ").lower().strip()
            if use_cache != 'y':
                cached_analyses = None
    
    analyses = []
    
    if cached_analyses:
        analyses = cached_analyses
    else:
        # 处理PDF
        print("\n📄 正在处理PDF...")
        
        with PDFProcessor(str(pdf_path), dpi=args.dpi) as processor:
            total_pages = processor.get_page_count()
            print(f"总页数: {total_pages}")
            
            # 解析页码范围
            try:
                pages_to_process = parse_page_range(args.pages, total_pages)
            except ValueError as e:
                print(f"❌ 错误: {e}")
                sys.exit(1)
            
            print(f"待处理页数: {len(pages_to_process)}")
            
            # 成本估算
            estimated_cost = estimate_cost(len(pages_to_process), args.llm)
            print(f"💰 预估成本: {estimated_cost}")
            
            # 确认继续
            if len(pages_to_process) > 5:
                confirm = input("\n是否继续? (y/n): ").lower().strip()
                if confirm != 'y':
                    print("已取消")
                    sys.exit(0)
            
            # 提取图像
            print("\n🖼️  正在提取页面图像...")
            image_paths = {}
            
            for page_num in tqdm(pages_to_process, desc="提取图像"):
                image = processor.extract_page_as_image(page_num)
                image_filename = f"page_{page_num:04d}.png"
                image_path = image_dir / image_filename
                image.save(image_path, 'PNG', optimize=True)
                image_paths[page_num] = str(image_path)
            
            # 创建LLM处理器
            print(f"\n🤖 正在使用 {args.llm} 分析课件...")
            llm_handler = create_llm_handler(args.llm, Config, args.prompt)
            
            # 分析每一页
            for page_num in tqdm(pages_to_process, desc="分析进度"):
                image_path = image_paths[page_num]
                
                # 可选:提取文本作为辅助上下文
                try:
                    text_content = processor.extract_text(page_num)
                    context = f"页面文本内容:\n{text_content[:500]}" if text_content.strip() else ""
                except:
                    context = ""
                
                # 调用LLM分析
                analysis = llm_handler.analyze_image(image_path, page_num, context)
                analyses.append((page_num, image_path, analysis))
                
                # 避免触发速率限制
                if page_num < pages_to_process[-1]:
                    time.sleep(1)
        
        # 保存缓存
        if Config.ENABLE_CACHE and not args.no_cache:
            print("\n💾 保存缓存...")
            output_generator.save_cache(analyses, str(cache_dir))
    
    # 生成输出文档
    print("\n📝 生成讲解文档...")
    
    output_files = []
    
    if args.format in ['markdown', 'both']:
        md_file = output_generator.generate_markdown(analyses)
        output_files.append(('Markdown', md_file))
        print(f"✅ Markdown: {md_file}")
    
    if args.format in ['html', 'both']:
        html_file = output_generator.generate_html(analyses)
        output_files.append(('HTML', html_file))
        print(f"✅ HTML: {html_file}")
    
    # 完成
    print(f"\n{'='*60}")
    print("🎉 处理完成!")
    print(f"{'='*60}")
    print(f"📊 统计信息:")
    print(f"  - 处理页数: {len(analyses)}")
    print(f"  - 图像文件: {image_dir}")
    print(f"  - 输出文档: {len(output_files)} 个")
    
    for format_name, file_path in output_files:
        print(f"    - {format_name}: {file_path}")
    
    print(f"\n💡 提示: 请查看生成的文档开始学习!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
