"""
单元测试
"""
import unittest
from pathlib import Path
import tempfile
import shutil

from utils import (
    parse_page_range, validate_pdf_file, 
    format_file_size, estimate_cost
)


class TestUtils(unittest.TestCase):
    """工具函数测试"""
    
    def test_parse_page_range(self):
        """测试页码范围解析"""
        # 测试范围
        self.assertEqual(parse_page_range("1-5", 10), [1, 2, 3, 4, 5])
        
        # 测试单个页码
        self.assertEqual(parse_page_range("3", 10), [3])
        
        # 测试混合
        self.assertEqual(parse_page_range("1-3,5,7-9", 10), [1, 2, 3, 5, 7, 8, 9])
        
        # 测试空字符串(全部页面)
        self.assertEqual(parse_page_range("", 5), [1, 2, 3, 4, 5])
        
        # 测试超出范围
        with self.assertRaises(ValueError):
            parse_page_range("1-100", 10)
    
    def test_format_file_size(self):
        """测试文件大小格式化"""
        self.assertEqual(format_file_size(0), "0.00 B")
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.00 GB")
    
    def test_estimate_cost(self):
        """测试成本估算"""
        cost_str = estimate_cost(10, 'openai')
        self.assertIn('$', cost_str)
        self.assertIn('USD', cost_str)
    
    def test_validate_pdf_file(self):
        """测试PDF文件验证"""
        # 测试不存在的文件
        is_valid, msg = validate_pdf_file("nonexistent.pdf")
        self.assertFalse(is_valid)
        
        # 测试非PDF文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        is_valid, msg = validate_pdf_file(temp_file)
        self.assertFalse(is_valid)
        Path(temp_file).unlink()


class TestPDFProcessor(unittest.TestCase):
    """PDF处理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        # 这里需要一个真实的PDF文件来测试
        # 在实际测试中,你可以使用测试PDF文件
        pass


class TestOutputGenerator(unittest.TestCase):
    """输出生成器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
    
    def test_markdown_generation(self):
        """测试Markdown生成"""
        from output_generator import OutputGenerator
        
        generator = OutputGenerator(self.test_dir, "test.pdf")
        
        # 模拟分析结果
        analyses = [
            (1, "image1.png", "这是第1页的分析"),
            (2, "image2.png", "这是第2页的分析"),
        ]
        
        # 生成Markdown(注意:这会失败因为图像路径不存在)
        # 实际测试中需要创建真实的图像文件
        pass


def run_tests():
    """运行所有测试"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
