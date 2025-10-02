#!/bin/bash
# Linux/Mac脚本 - 快速运行PDF分析器

echo "========================================"
echo "  PDF课件自动讲解系统"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3,请先安装Python 3.8+"
    exit 1
fi

# 创建虚拟环境(如果不存在)
if [ ! -d "venv" ]; then
    echo "[提示] 首次运行,正在创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[提示] 正在安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "[警告] 未找到.env文件"
    echo "[提示] 正在从.env.example创建.env文件..."
    cp .env.example .env
    echo ""
    echo "[重要] 请编辑.env文件,填入你的API密钥后再运行!"
    echo ""
    exit 1
fi

# 运行主程序
if [ $# -eq 0 ]; then
    echo "用法: ./run.sh 你的课件.pdf [选项]"
    echo ""
    echo "示例:"
    echo "  ./run.sh lecture.pdf"
    echo "  ./run.sh lecture.pdf --llm openai"
    echo "  ./run.sh lecture.pdf --pages 1-5"
    echo ""
    python3 main.py --help
else
    python3 main.py "$@"
fi
