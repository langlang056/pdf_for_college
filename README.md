# PDF课件自动讲解系统

一个自动化处理PDF课件的工具,能够逐页分析课件内容并生成详细讲解。

## 功能特性

- 📄 自动将PDF每一页转换为图像
- 🤖 使用多模态LLM分析每页内容
- 📝 生成结构化的Markdown讲解文档
- 💾 支持缓存,避免重复处理
- 🔄 支持多种LLM后端 (OpenAI, Claude, Gemini等)
- 📊 实时进度显示
- ⚡ 支持并发处理提高效率

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 到 `.env` 并填入你的API密钥:

```bash
cp .env.example .env
```

编辑 `.env` 文件,添加你的API密钥:

```
OPENAI_API_KEY=your_openai_api_key_here
# 或者使用其他LLM提供商
# ANTHROPIC_API_KEY=your_claude_api_key
# GOOGLE_API_KEY=your_gemini_api_key
```

## 使用方法

### 基础使用

```bash
python main.py path/to/your/lecture.pdf
```

### 指定输出目录

```bash
python main.py lecture.pdf -o output_folder
```

### 选择LLM提供商

```bash
# 使用OpenAI (默认)
python main.py lecture.pdf --llm openai

# 使用Claude
python main.py lecture.pdf --llm claude

# 使用Gemini
python main.py lecture.pdf --llm gemini
```

### 自定义提示词

```bash
python main.py lecture.pdf --prompt "请详细解释这一页课件的内容,重点关注数学公式和定理"
```

### 处理特定页面范围

```bash
# 只处理第1-10页
python main.py lecture.pdf --pages 1-10

# 处理特定页面
python main.py lecture.pdf --pages 1,3,5,7
```

## 输出结果

处理完成后会在输出目录生成:

- `lecture_explained.md` - 完整的讲解文档
- `images/` - 每页的图像文件
- `cache/` - 缓存文件(可删除以重新处理)

## 项目结构

```
pdf_analyser/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── pdf_processor.py     # PDF处理模块
├── llm_handler.py       # LLM交互模块
├── output_generator.py  # 输出生成模块
├── utils.py             # 工具函数
├── requirements.txt     # 依赖列表
├── .env.example        # 环境变量模板
└── README.md           # 项目文档
```

## 高级配置

编辑 `config.py` 可以自定义:

- LLM模型选择
- 图像质量和分辨率
- 并发处理数量
- 缓存策略
- 自定义提示词模板

## 注意事项

1. **API成本**: 使用LLM API会产生费用,建议先小范围测试
2. **图像质量**: 高分辨率图像会提供更好的分析结果,但会增加API成本
3. **速率限制**: 注意API提供商的速率限制,程序会自动处理重试

## 许可证

MIT License
