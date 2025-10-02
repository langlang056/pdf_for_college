@echo off
REM Windows批处理脚本 - 快速运行PDF分析器

echo ========================================
echo   PDF课件自动讲解系统
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python,请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否已安装依赖
if not exist "venv\" (
    echo [提示] 首次运行,正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM 检查.env文件
if not exist ".env" (
    echo [警告] 未找到.env文件
    echo [提示] 正在从.env.example创建.env文件...
    copy .env.example .env
    echo.
    echo [重要] 请编辑.env文件,填入你的API密钥后再运行!
    echo.
    pause
    exit /b 1
)

REM 运行主程序
if "%~1"=="" (
    echo 用法: run.bat 你的课件.pdf [选项]
    echo.
    echo 示例:
    echo   run.bat lecture.pdf
    echo   run.bat lecture.pdf --llm openai
    echo   run.bat lecture.pdf --pages 1-5
    echo.
    python main.py --help
) else (
    python main.py %*
)

pause
